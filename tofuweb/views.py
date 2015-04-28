import os
from tofuweb import app, admin, db
from tofuweb.models import Dataset, Reconstruction, MapSliceModel
from tofuweb.proc import RecoProcess, DownsizeProcess, MapProcess, reco_path
from flask import request, render_template, redirect, url_for, jsonify, send_from_directory
from flask.ext.admin.contrib.sqla import ModelView
from wtforms import Form, TextField, FloatField, validators

admin.add_view(ModelView(Dataset, db.session))
admin.add_view(ModelView(Reconstruction, db.session))
admin.add_view(ModelView(MapSliceModel, db.session))

class CreateForm(Form):
    name = TextField("Name", [validators.Required()])
    radios = TextField("Radios", [validators.Required()])
    darks = TextField("Darks")
    flats = TextField("Flats")


class RecoForm(Form):
    axis = FloatField("axis")


@app.route('/')
def index():
    datasets = Dataset.query.all()
    reconstructions = Reconstruction.query.all()
    form = CreateForm(request.form)
    data = dict(datasets=datasets, recos=reconstructions, create_form=form)
    return render_template('index.html', **data)


@app.route('/data/<int:dataset_id>')
def show_dataset(dataset_id):
    dataset = Dataset.query.filter_by(id=dataset_id).first()
    return render_template('show.html', dataset=dataset)


@app.route('/data/create', methods=['POST'])
def create_dataset():
    form = CreateForm(request.form)

    if form.validate:
        dataset = Dataset(form.name.data, form.radios.data, darks=form.darks.data, flats=form.flats.data)
        db.session.add(dataset)
        db.session.commit()

    return redirect(url_for('index'))


@app.route('/data/delete/<int:dataset_id>')
def delete_dataset(dataset_id):
    dataset = Dataset.query.filter_by(id=dataset_id).first()
    db.session.delete(dataset)
    db.session.commit()
    return redirect(url_for('index'))


@app.route('/data/reconstruct/<int:dataset_id>', methods=['POST'])
def reconstruct(dataset_id):
    form = RecoForm(request.form)
    dataset = Dataset.query.filter_by(id=dataset_id).first()
    reco = Reconstruction(dataset, axis=form.axis.data)
    db.session.add(reco)
    db.session.commit()

    recoProc = RecoProcess(reco)
    recoProc.start()

    return redirect(url_for('index'))


@app.route('/reco/<int:reco_id>')
def show_reconstruction(reco_id):
    reconstruction = Reconstruction.query.filter_by(id=reco_id).first()
    return render_template('reco.html', reconstruction=reconstruction)


@app.route('/reco/delete/<int:dataset_id>')
def delete_reconstruction(dataset_id):
    reco = Reconstruction.query.filter_by(id=dataset_id).first()

    try:
        import shutil
        shutil.rmtree(reco.getPath())
    except OSError, e:
        print("Dir of reconstruction can't be deleted or not found!")

    for entity in reco.maps_slices:
        db.session.delete(entity)
    db.session.delete(reco)
    db.session.commit()
    return redirect(url_for('index'))


@app.route('/reco/<int:dataset_id>/done')
def reconstruction_done(dataset_id):
    dataset = Reconstruction.query.filter_by(id=dataset_id).first()
    return jsonify(done=dataset.done)


@app.route('/reco/<int:dataset_id>.tif')
def download(dataset_id):
    dataset = Reconstruction.query.filter_by(id=dataset_id).first()
    path = os.path.abspath(reco_path(dataset))
    return send_from_directory(path, 'slice-00000.tif', as_attachment=True)


@app.route('/reco/<int:dataset_id>/slice')
def downsize(dataset_id):
    dataset = Reconstruction.query.filter_by(id=dataset_id).first()
    downsize = DownsizeProcess(dataset)
    downsize.start()
    return jsonify({})

@app.route('/reco/<int:reco_id>/map.jpg')
def slice_map(reco_id):
    reco = Reconstruction.query.filter_by(id=reco_id).first()

    try:
        map_slice = reco.maps_slices[0]
    except:
        mapProc = MapProcess(db, reco)
        mapProc.start()
        mapProc.join()
        map_slice = reco.maps_slices[0]

    return send_from_directory(map_slice.path, map_slice.map_file_name)


@app.route('/reco/<int:dataset_id>/slice/<int:number>')
def get_slice(dataset_id, number):
    dataset = Reconstruction.query.filter_by(id=dataset_id).first()
    path = os.path.abspath(reco_path(dataset))
    return send_from_directory(os.path.join(path, 'web'), 'map-%05i.jpg' % number)

@app.route('/reco/<int:reco_id>/render')
def render(reco_id):
    reco = Reconstruction.query.filter_by(id=reco_id).first()
    
    try:
        map_slice = reco.maps_slices[0]
    except:
        mapProc = MapProcess(db, reco)
        mapProc.start()
        mapProc.join()
        map_slice = reco.maps_slices[0]

    return render_template('congote_native_webgl.html', reco_id=reco_id, reco=reco, map_slice=map_slice)
