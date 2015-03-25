import os
import multiprocessing
from tofuweb import app, db


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
            app.logger.debug("Finished reconstruction in {}s".format(time))
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

        path = reco_path(self.reconstruction)
        read = Read(path=os.path.join(path, 'slice*.tif'))
        rescale = Rescale(factor=0.5)
        edge = DetectEdge()
        write = Write(filename=os.path.join(path, 'web', 'map-%05i.jpg'), bits=8)
        write(rescale(square(edge(read())))).run().join()
