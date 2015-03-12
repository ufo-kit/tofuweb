import os
import time
import multiprocessing
from tofuweb import app, admin, db
from tofuweb.models import Raw, Reconstruction, Surface
from flask import request, render_template, redirect, url_for, jsonify, send_from_directory, send_file
from flask.ext.admin.contrib.sqla import ModelView
from wtforms import Form, TextField, FloatField, validators


admin.add_view(ModelView(Raw, db.session))
admin.add_view(ModelView(Reconstruction, db.session))


def reco_path(reco_dataset):
    return os.path.join('/tmp/recos/', str(reco_dataset.raw.id), str(reco_dataset.id))


def texture_path(reco_dataset):
    return os.path.join(reco_path(reco_dataset), 'textures', 'texture.jpg')


class CreateForm(Form):
    name = TextField("Name", [validators.Required()])
    radios = TextField("Radios", [validators.Required()])
    darks = TextField("Darks")
    flats = TextField("Flats")


class RecoForm(Form):
    axis = FloatField("axis")


class RecoProcess(multiprocessing.Process):

    def __init__(self, dataset):
        super(RecoProcess, self).__init__()
        self.dataset = dataset

    def run(self):
        from tofu import reco, config, __version__

        output = os.path.join(reco_path(self.dataset), 'volume.tif')
        app.logger.debug("Write output to {}".format(output))
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


class SurfaceProcess(multiprocessing.Process):

    def __init__(self, surface):
        super(SurfaceProcess, self).__init__()
        self.surface = surface

    def run(self):
        import vtk, vtk.io
        path = reco_path(self.surface.reco)

        reader = vtk.io.vtkTIFFReader()
        reader.SetFileName(os.path.join(path, 'volume.tif'))
        reader.Update()

        threshold = vtk.vtkImageThreshold()
        threshold.SetInputConnection(reader.GetOutputPort())
        threshold.ThresholdByLower(400)
        threshold.ReplaceInOn()
        threshold.SetInValue(0)
        threshold.ReplaceOutOn()
        threshold.SetOutValue(1)
        threshold.Update()

        dmc = vtk.vtkDiscreteMarchingCubes()
        dmc.SetInputConnection(threshold.GetOutputPort())
        dmc.GenerateValues(1, 1, 1)
        dmc.Update()

        writer = vtk.vtkSTLWriter()
        writer.SetInputConnection(dmc.GetOutputPort())
        writer.SetFileTypeToBinary()
        writer.SetFileName(os.path.join(path, 'mesh.stl'))
        writer.Write()


@app.route('/')
def index():
    raw_datasets = Raw.query.all()
    reconstructions = Reconstruction.query.all()
    data = dict(raw_datasets=raw_datasets, recos=reconstructions)
    return render_template('index.html', **data)


@app.route('/raw/show/<int:dataset_id>')
def show_raw_dataset(dataset_id):
    dataset = Raw.query.filter_by(id=dataset_id).first()
    return render_template('show.html', dataset=dataset)


@app.route('/raw/create', methods=['GET', 'POST'])
def create_raw_dataset():
    form = CreateForm(request.form)

    if request.method == 'POST' and form.validate:
        dataset = Raw(form.name.data, form.radios.data, darks=form.darks.data, flats=form.flats.data)
        db.session.add(dataset)
        db.session.commit()
        return redirect(url_for('index'))
    else:
        return render_template('create.html', form=form)


@app.route('/raw/delete/<int:dataset_id>')
def delete_raw_dataset(dataset_id):
    dataset = Raw.query.filter_by(id=dataset_id).first()
    db.session.delete(dataset)
    db.session.commit()
    return redirect(url_for('index'))


@app.route('/raw/reconstruct/<int:dataset_id>', methods=['POST'])
def reconstruct(dataset_id):
    form = RecoForm(request.form)
    dataset = Raw.query.filter_by(id=dataset_id).first()
    reco_dataset = Reconstruction(dataset, axis=form.axis.data)
    db.session.add(reco_dataset)
    db.session.commit()

    reco = RecoProcess(reco_dataset)
    reco.start()

    return redirect(url_for('index'))


@app.route('/reco/show/<int:dataset_id>')
def show_reconstruction(dataset_id):
    dataset = Reconstruction.query.filter_by(id=dataset_id).first()
    return render_template('reco.html', dataset=dataset)


@app.route('/reco/delete/<int:dataset_id>')
def delete_reconstruction(dataset_id):
    dataset = Reconstruction.query.filter_by(id=dataset_id).first()
    db.session.delete(dataset)
    db.session.commit()
    return redirect(url_for('index'))


@app.route('/reco/done/<int:dataset_id>')
def reconstruction_done(dataset_id):
    dataset = Reconstruction.query.filter_by(id=dataset_id).first()
    return jsonify(done=dataset.done)


@app.route('/reco/download/<int:dataset_id>')
def download(dataset_id):
    dataset = Reconstruction.query.filter_by(id=dataset_id).first()
    path = os.path.abspath(reco_path(dataset))
    return send_from_directory(path, 'volume.tif', as_attachment=True)


@app.route('/reco/render/<int:dataset_id>')
def render(dataset_id):
    dataset = Reconstruction.query.filter_by(id=dataset_id).first()
    return render_template('render.html', dataset=dataset)


@app.route('/reco/<int:dataset_id>/volume.stl')
def get_mesh(dataset_id):
    dataset = Reconstruction.query.filter_by(id=dataset_id).first()
    path = os.path.abspath(reco_path(dataset))
    return send_from_directory(path, 'volume.stl')


@app.route('/reco/mesh/<int:dataset_id>')
def generate_mesh(dataset_id):
    dataset = Reconstruction.query.filter_by(id=dataset_id).first()

    surface = Surface(dataset)
    map_process = SurfaceProcess(surface)
    map_process.start()

    return jsonify(generating=True)
