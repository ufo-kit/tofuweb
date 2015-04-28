import os
import multiprocessing
from tofuweb import app, db
from tofuweb.models import SliceMap

def reco_path(reco):
    return os.path.join('/tmp/recos/', str(reco.dataset.id), str(reco.id))


class RecoProcess(multiprocessing.Process):

    def __init__(self, reco):
        name = 'reco-{}'.format(reco.dataset.id)
        super(RecoProcess, self).__init__(name=name)
        self.reco = reco

    def run(self):
        from tofu import reco, config, __version__

        try:
            self.reco.creation_going = True

            output = os.path.join(reco_path(self.reco), 'slice-%05i.tif')
            params = config.TomoParams().get_defaults()
            params.axis = self.reco.axis
            params.input = self.reco.dataset.data_path
            params.darks = self.reco.dataset.darks_path
            params.flats = self.reco.dataset.flats_path
            params.output = output
            params.from_projections = True

            app.logger.info("|- Start reconstruction of reco.id={}.\n"\
            "|- axis           :{}\n"\
            "|- data path      :{}\n"\
            "|- darks path     :{}\n"\
            "|- flats path     :{}\n"\
            "|- output path    :{}\n"\
            .format(self.reco.id, self.reco.axis, self.reco.dataset.data_path, self.reco.dataset.darks_path, self.reco.dataset.flats_path, output))

            # raise Exception("!!!")

            time = reco.tomo(params)
            self.reco.time = time
            
            self.reco.creation_going = False
            self.reco.has_error = False

            app.logger.debug("Finished reconstruction for reco.id={} in {} s.".format(self.reco.id, self.reco.time))

        except Exception as e:
            self.reco.has_error = True
            app.logger.error("Crashed reconstruction for reco.id={}. Error: {}".format(self.reco.id, e))

        finally:
            self.reco.done = True
            self.reco.software = 'Tofu {}'.format(__version__)
            db.session.commit()

class SlicesThumbsProcess(multiprocessing.Process):

    def __init__(self, slices_thumbs):
        super(SlicesThumbsProcess, self).__init__()
        self.slices_thumbs = slices_thumbs

    def run(self):
        from ufo import Read, Rescale, Write
        import math
        import time

        app.logger.info("|- Start creation slice thumbs for reco.id={}.\n"\
        "|- path to slices :{}\n"\
        "|- path to thumbs :{}\n"\
        .format(self.slices_thumbs.reco.id, self.slices_thumbs.reco.path_to_slices, self.slices_thumbs.path_to_thumbs))

        try:
            start_time = time.time()
            self.slices_thumbs.creation_going = True
            db.session.commit()

            if not(os.path.exists(os.path.join(self.slices_thumbs.reco.path_to_dir, 'slice-00000.tif'))):
                raise Exception("Slices do not exists in the path: {}".format(self.slices_thumbs.reco.path_to_dir))
            
            # Read slices
            read = Read(path=self.slices_thumbs.reco.path_to_slices)
            rescale = Rescale(factor=1.0)

            write = Write(filename=self.slices_thumbs.path_to_thumbs, bits=8)
            write(
                rescale(
                    read()
                )
            ).run().join()

            self.slices_thumbs.slices_number = len(os.listdir(self.slices_thumbs.reco.path_to_dir))-3

            self.slices_thumbs.has_error = False
            self.slices_thumbs.creation_going = False

            self.slices_thumbs.time = time.time() - start_time

            app.logger.debug("Finished slices thumbs creation for reco.id={} in {} s.".format(self.slices_thumbs.reco.id, self.slices_thumbs.time))

        except Exception as e:
            self.slices_thumbs.has_error = True
            app.logger.error("Crashed slices thumbs creation for reco.id={}. Error: {}".format(self.slices_thumbs.reco.id, e))

        finally:
            self.slices_thumbs.done = True
            db.session.commit()


class SliceMapProcess(multiprocessing.Process):
    def __init__(self, slice_map):
        super(SliceMapProcess, self).__init__()
        self.slice_map = slice_map

    def run(self):
        from ufo import Read, MapSlice, Rescale, Write
        import tifffile
        import math
        import time

        try:
            start_time = time.time()

            self.slice_map.creation_going = True
            db.session.commit()

            if not(os.path.exists(os.path.join(self.slice_map.reco.path_to_dir, 'slice-00000.tif'))):
                raise Exception("Slices do not exists in the path: {}".format(self.slice_map.reco.path_to_dir))

            reco_dir = self.slice_map.reco.path_to_dir
            slice_map_files = os.listdir(reco_dir)
            slices_number = len(slice_map_files) - 3

            self.slice_map.slices_number = slices_number

            app.logger.info("|- Start creation slice map for reco.id={}.\n"\
            "|- reco_dir       :{}\n"\
            "|- slice_map_files:{} ... {}\n"\
            "|- slices_number  :{}".format(self.slice_map.reco_id, reco_dir, slice_map_files[0:3], slice_map_files[-1], slices_number))
            
            im = tifffile.imread(os.path.join(reco_dir, slice_map_files[0]))
            
            self.slice_map.original_slice_height, self.slice_map.original_slice_width = im.shape

            self.slice_map.sliceMap_slices_per_row = math.ceil(math.sqrt(self.slice_map.slices_number))
            self.slice_map.sliceMap_slices_per_col = self.slice_map.sliceMap_slices_per_row

            self.slice_map.resize_factor = (self.slice_map.sliceMap_width/self.slice_map.sliceMap_slices_per_row) / self.slice_map.original_slice_width

            self.slice_map.sliceMap_slice_width = self.slice_map.original_slice_width * self.slice_map.resize_factor
            self.slice_map.sliceMap_slice_height = self.slice_map.original_slice_height * self.slice_map.resize_factor

            # Read slices
            read = Read(path=self.slice_map.reco.path_to_dir, number=self.slice_map.slices_number)

            # raise Exception("!!!")
            
            # Rescale slices
            rescale = Rescale(factor=self.slice_map.resize_factor)
            
            slice_map = MapSlice(number=self.slice_map.slices_number)
            
            # Write slice map
            path_to_slice_map = os.path.join(self.slice_map.path_to_dir, "slice_map.jpg")
            write = Write(filename=path_to_slice_map, bits=8)
            write(
                slice_map(
                    rescale(
                        read()
                    )
                )
            ).run().join()

            self.slice_map.has_error = False
            self.slice_map.creation_going = False

            self.slice_map.time = time.time() - start_time

            app.logger.debug("|- Finished slice map creation for reco.id={} in {} s.".format(self.slice_map.reco_id, self.slice_map.time))

        except Exception as e:
            import linecache
            import sys

            exc_type, exc_obj, tb = sys.exc_info()
            lineno = tb.tb_lineno
            # print("Exception: {}".format(lineno))

            self.slice_map.has_error = True
            app.logger.error("Crashed slice map creation for reco.id={}. Error: {}. Line: {}".format(self.slice_map.reco_id, e, lineno))

        finally:
            self.slice_map.done = True
            db.session.commit()