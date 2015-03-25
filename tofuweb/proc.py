import os
import multiprocessing
from tofuweb import app, db


def reco_path(reco_dataset):
    return os.path.join('/tmp/recos/', str(reco_dataset.raw.id), str(reco_dataset.id))


class RecoProcess(multiprocessing.Process):

    def __init__(self, dataset):
        name = 'reco-{}'.format(dataset.raw.id)
        super(RecoProcess, self).__init__(name=name)
        self.dataset = dataset

    def run(self):
        from tofu import reco, config, __version__

        output = os.path.join(reco_path(self.dataset), 'slice-%05i.tif')
        params = config.TomoParams().get_defaults()
        params.axis = self.dataset.axis
        params.input = self.dataset.raw.data_path
        params.darks = self.dataset.raw.darks_path
        params.flats = self.dataset.raw.flats_path
        params.output = output
        params.from_projections = True

        try:
            time = reco.tomo(params)
            app.logger.debug("Finished reconstruction in {}s".format(time))
        finally:
            self.dataset.software = 'Tofu {}'.format(__version__)
            self.dataset.time = time
            self.dataset.done = True
            db.session.commit()


class DownsizeProcess(multiprocessing.Process):

    def __init__(self, dataset):
        super(DownsizeProcess, self).__init__()
        self.dataset = dataset

    def run(self):
        from ufo import Read, DetectEdge, Rescale, Write

        path = reco_path(self.dataset)

        read = Read(path=os.path.join(path, 'slice*.tif'))
        rescale = Rescale(factor=0.25)
        write = Write(filename=os.path.join(path, 'web', 'map-%05i.jpg'), bits=8)
        app.logger.info("Downsizing for web")
        write(rescale(read())).run().join()
