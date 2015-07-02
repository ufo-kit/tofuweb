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

        app.logger.debug("Start reconstruction of reco.id={}".format(self.reco.id))

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
        from ufo import Read, DetectEdge, Rescale, Write
        import math
        import time

        app.logger.debug("Start creation slice thumbs for reco.id={}".format(self.slices_thumbs.reco.id))

        try:
            start_time = time.time()
            self.slices_thumbs.creation_going = True
            db.session.commit()

            if not(os.path.exists(os.path.join(self.slices_thumbs.reco.getPathToDir(), 'slice-00000.tif'))):
                raise Exception("Slices do not exists in the path: {}".format(self.slices_thumbs.reco.getPathToDir()))
            
            # Read slices
            read = Read(path=self.slices_thumbs.reco.getPathToSlices())
            
            rescale = Rescale(factor=1.0)
            # edge = DetectEdge()
            write = Write(filename=self.slices_thumbs.getPathToThumbs(), bits=8)
            write(
                rescale(
                    # edge(
                        read()
                    # )
                )
            ).run().join()

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
        from PIL import Image
        import math
        import time
        
        app.logger.debug("Start creation slice map for reco.id={}".format(self.slice_map.reco.id))

        try:
            start_time = time.time()

            self.slice_map.creation_going = True
            db.session.commit()

            if not(os.path.exists(os.path.join(self.slice_map.reco.getPathToDir(), 'slice-00000.tif'))):
                raise Exception("Slices do not exists in the path: {}".format(self.slice_map.reco.getPathToDir()))

            self.slice_map.slices_number = len(os.listdir(self.slice_map.reco.getPathToDir()))
            
            im = Image.open(os.path.join(self.slice_map.reco.getPathToDir(),os.listdir(self.slice_map.reco.getPathToDir())[0]))
            sliceResolution = im.size
            
            self.slice_map.original_slice_width = sliceResolution[0]
            self.slice_map.original_slice_height = sliceResolution[1]

            self.slice_map.sliceMap_slices_per_row = math.ceil(math.sqrt(self.slice_map.slices_number))
            self.slice_map.sliceMap_slices_per_col = self.slice_map.sliceMap_slices_per_row

            self.slice_map.resize_factor = (self.slice_map.sliceMap_width/self.slice_map.sliceMap_slices_per_row) / self.slice_map.original_slice_width

            self.slice_map.sliceMap_slice_width = self.slice_map.original_slice_width * self.slice_map.resize_factor
            self.slice_map.sliceMap_slice_height = self.slice_map.original_slice_height * self.slice_map.resize_factor

            # Read slices
            read = Read(path=self.slice_map.reco.getPathToDir(), number=self.slice_map.slices_number)

            # raise Exception("!!!")
            
            # Rescale slices
            rescale = Rescale(factor=self.slice_map.resize_factor)
            
            slice_map = MapSlice(number=self.slice_map.slices_number)
            
            # Write slice map
            pathToSliceMap = os.path.join(self.slice_map.getPathToDir(), "slice_map.jpg")
            write = Write(filename=pathToSliceMap, bits=8)
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

            app.logger.debug("Finished slice map creation for reco.id={} in {} s.".format(self.slice_map.reco_id, self.slice_map.time))

        except Exception as e:
            self.slice_map.has_error = True
            app.logger.error("Crashed slice map creation for reco.id={}. Error: {}".format(self.slice_map.reco_id, e))

        finally:
            self.slice_map.done = True
            db.session.commit()
