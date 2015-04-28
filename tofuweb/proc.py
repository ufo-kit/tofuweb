import os
import multiprocessing
from tofuweb import app, db
from tofuweb.models import MapSliceModel

def reco_path(reconstruction):
    return os.path.join('/tmp/recos/', str(reconstruction.dataset.id), str(reconstruction.id))


class RecoProcess(multiprocessing.Process):

    def __init__(self, reconstruction):
        name = 'reco-{}'.format(reconstruction.dataset.id)
        super(RecoProcess, self).__init__(name=name)
        self.reconstruction = reconstruction

    def run(self):
        from tofu import reco, config, __version__

        output = os.path.join(reco_path(self.reconstruction), 'slice-%05i.tif')
        params = config.TomoParams().get_defaults()
        params.axis = self.reconstruction.axis
        params.input = self.reconstruction.dataset.data_path
        params.darks = self.reconstruction.dataset.darks_path
        params.flats = self.reconstruction.dataset.flats_path
        params.output = output
        params.from_projections = True

        try:
            time = reco.tomo(params)
            app.logger.debug("Finished reconstruction in {}".format(time))
        finally:
            self.reconstruction.software = 'Tofu {}'.format(__version__)
            self.reconstruction.time = time
            self.reconstruction.done = True
            db.session.commit()


class DownsizeProcess(multiprocessing.Process):

    def __init__(self, reconstruction):
        super(DownsizeProcess, self).__init__()
        self.reconstruction = reconstruction

    def run(self):
        from ufo import Read, DetectEdge, Rescale, Write

        print("DownsizeProcess.run");

        path = reco_path(self.reconstruction)
        read = Read(path=os.path.join(path, 'slice*.tif'))
        rescale = Rescale(factor=1.0)
        edge = DetectEdge()
        write = Write(filename=os.path.join(path, 'web', 'map-%05i.jpg'), bits=8)
        write(rescale(edge(read()))).run().join()


class MapProcess(multiprocessing.Process):
    def __init__(self, db, reco):
        super(MapProcess, self).__init__()
        self.db = db
        self.reco = reco

    def run(self):
        from ufo import Read, MapSlice, Rescale, Write
        from PIL import Image
        import math
        import time

        map_slice_model = MapSliceModel(self.reco)
        
        start_time = time.time()        
        
        map_slice_model.path = os.path.join(self.reco.getPath(), "web")
        map_slice_model.slices_number = len(os.listdir(self.reco.getPath()))

        map_slice_model.sliceMap_width = 4096
        map_slice_model.sliceMap_height = 4096
        
        im = Image.open(os.path.join(self.reco.getPath(),os.listdir(self.reco.getPath())[0]))
        sliceResolution = im.size
        
        map_slice_model.original_slice_width = sliceResolution[0]
        map_slice_model.original_slice_height = sliceResolution[1]

        map_slice_model.sliceMap_slices_per_row = math.ceil(math.sqrt(map_slice_model.slices_number))
        map_slice_model.sliceMap_slices_per_col = map_slice_model.sliceMap_slices_per_row

        map_slice_model.resize_factor = (map_slice_model.sliceMap_width/map_slice_model.sliceMap_slices_per_row) / map_slice_model.original_slice_width

        map_slice_model.sliceMap_slice_width = map_slice_model.original_slice_width * map_slice_model.resize_factor
        map_slice_model.sliceMap_slice_height = map_slice_model.original_slice_height * map_slice_model.resize_factor
        
        read = Read(path=os.path.join(self.reco.getPath(), 'slice*.tif'), number=map_slice_model.slices_number)
        rescale = Rescale(factor=map_slice_model.resize_factor)
        map_slices = MapSlice(number=map_slice_model.slices_number)
        write = Write(filename=os.path.join(map_slice_model.path, map_slice_model.map_file_name), bits=8)
        write(map_slices(rescale((read())))).run().join()

        map_slice_model.done = True
        map_slice_model.time = time.time() - start_time

        db.session.add(map_slice_model)
        db.session.commit()
