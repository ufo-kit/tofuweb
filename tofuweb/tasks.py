from tofuweb import app, db
from tofuweb.models import Reconstruction
from celery import Celery
import os


celery = Celery('tofuweb.tasks')
celery.conf.update(app.config)


def reco_path(reconstruction):
    return os.path.join('/tmp/recos/', str(reconstruction.dataset.id), str(reconstruction.id))


@celery.task
def reconstruct(reco_id):
    from tofu import reco, config, __version__

    reconstruction = Reconstruction.query.filter_by(id=reco_id).first()

    output = os.path.join(reco_path(reconstruction), 'slice-%05i.tif')
    params = config.TomoParams().get_defaults()
    params.axis = reconstruction.axis
    params.input = reconstruction.dataset.data_path
    params.darks = reconstruction.dataset.darks_path
    params.flats = reconstruction.dataset.flats_path
    params.output = output
    params.from_projections = True

    try:
        time = reco.tomo(params)
        reconstruction.time = time
        app.logger.debug("Finished reconstruction in {}s".format(time))
    finally:
        reconstruction.software = 'Tofu {}'.format(__version__)
        reconstruction.done = True
        db.session.commit()
