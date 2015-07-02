import os
from tofuweb import app, admin, db
from tofuweb.models import Dataset, Reconstruction, SliceMap, SlicesThumbs
from tofuweb.proc import RecoProcess, SlicesThumbsProcess, SliceMapProcess, reco_path
from flask import request, render_template, redirect, url_for, jsonify, send_from_directory
from flask.ext.admin.contrib.sqla import ModelView
from wtforms import Form, TextField, FloatField, validators

admin.add_view(ModelView(Dataset, db.session))
admin.add_view(ModelView(Reconstruction, db.session))
admin.add_view(ModelView(SliceMap, db.session))
admin.add_view(ModelView(SlicesThumbs, db.session))

class CreateForm(Form):
    name = TextField("Name", [validators.Required()])
    radios = TextField("Radios", [validators.Required()])
    darks = TextField("Darks")
    flats = TextField("Flats")


class RecoForm(Form):
    axis = FloatField("axis")


@app.route('/')
def index():
    try:
        datasets = Dataset.query.all()
        reconstructions = Reconstruction.query.all()
        form = CreateForm(request.form)
        data = dict(datasets=datasets, recos=reconstructions, create_form=form)
        return render_template('index.html', **data)

    except Exception as e:
        app.logger.error("Crashed query: /: Error: {}".format(e))
        return render_template('error.html', error_message=e)


@app.route('/data/<int:dataset_id>')
def show_dataset(dataset_id):
    try:
        dataset = Dataset.query.filter_by(id=dataset_id).first()
        return render_template('show.html', dataset=dataset)
        
    except Exception as e:
        app.logger.error("Crashed query: /data/{}: Error: {}".format(dataset_id, e))
        return render_template('error.html', error_message=e)


@app.route('/data/create', methods=['POST'])
def create_dataset():
    try:
        form = CreateForm(request.form)

        if form.validate:
            dataset = Dataset(form.name.data, form.radios.data, darks=form.darks.data, flats=form.flats.data)
            db.session.add(dataset)
            db.session.commit()

        return redirect(url_for('index'))

    except Exception as e:
        app.logger.error("Crashed query: /data/create: Error: {}".format(e))
        return render_template('error.html', error_message=e)


@app.route('/data/delete/<int:dataset_id>')
def delete_dataset(dataset_id):
    try:
        dataset = Dataset.query.filter_by(id=dataset_id).first()
        db.session.delete(dataset)
        db.session.commit()
        return redirect(url_for('index'))
        
    except Exception as e:
        app.logger.error("Crashed query: /data/delete/{}: Error: {}".format(dataset_id, e))
        return render_template('error.html', error_message=e)


@app.route('/data/reconstruct/<int:dataset_id>', methods=['POST'])
def reconstruct(dataset_id):
    try:
        form = RecoForm(request.form)

        dataset = Dataset.query.filter_by(id=dataset_id).first()

        reco = Reconstruction(dataset, axis=form.axis.data)
        db.session.add(reco)
        db.session.commit()

        slice_map = SliceMap(reco)
        db.session.add(slice_map)
        db.session.commit()

        slices_thumbs = SlicesThumbs(reco)
        db.session.add(slices_thumbs)
        db.session.commit()

        recoProc = RecoProcess(reco)
        recoProc.start()

        return redirect(url_for('index'))
        
    except Exception as e:
        app.logger.error("Crashed query: /data/reconstruction/{}: Error: {}".format(dataset_id, e))
        return render_template('error.html', error_message=e)


@app.route('/reco/<int:reco_id>')
def show_reconstruction(reco_id):
    try:
        reconstruction = Reconstruction.query.filter_by(id=reco_id).first()
        return render_template('reco.html', reconstruction=reconstruction)
        
    except Exception as e:
        app.logger.error("Crashed query: /reco/{}: Error: {}".format(reco_id, e))
        return render_template('error.html', error_message=e)


@app.route('/reco/delete/<int:dataset_id>')
def delete_reconstruction(dataset_id):
    try:
        reco = Reconstruction.query.filter_by(id=dataset_id).first()

        try:
            import shutil
            shutil.rmtree(reco.getPathToDir())
        except OSError, e:
            app.logger.error("Dir of reconstruction can't be deleted or not found!")


        for entity in reco.maps_slices:
            db.session.delete(entity)

        for entity in reco.slices_thumbs:
            db.session.delete(entity)

        db.session.delete(reco)
        db.session.commit()
        return redirect(url_for('index'))

    except Exception as e:
        app.logger.error("Crashed query: /reco/delete/{}: Error: {}".format(dataset_id, e))
        return render_template('error.html', error_message=e)



@app.route('/reco/<int:reco_id>/done')
def reconstruction_done(reco_id):
    try:
        reco = Reconstruction.query.filter_by(id=reco_id).first()
        slice_map = SliceMap.query.filter_by(reco_id=reco.id).first()
        slices_thumbs = SlicesThumbs.query.filter_by(reco_id=reco.id).first()

        if reco.done == True:
            if slice_map.done == False and slice_map.creation_going == False:
                slice_map_proc = SliceMapProcess(slice_map)
                slice_map_proc.start()

            if slices_thumbs.done == False and slices_thumbs.creation_going == False:
                slices_thumbs_proc = SlicesThumbsProcess(slices_thumbs)
                slices_thumbs_proc.start()

        return jsonify(reco_done=reco.done, reco_has_error=reco.has_error, slice_map_done=slice_map.done, slice_map_has_error=slice_map.has_error, slices_thumbs_done=slices_thumbs.done, slices_thumbs_has_error=slices_thumbs.has_error)
        
    except Exception as e:
        app.logger.error("Crashed query: /reco/{}/done: Error: {}".format(reco_id, e))
        return render_template('error.html', error_message=e)


@app.route('/reco/<int:dataset_id>.tif')
def download(dataset_id):
    try:
        dataset = Reconstruction.query.filter_by(id=dataset_id).first()
        path = os.path.abspath(reco_path(dataset))
        return send_from_directory(path, 'slice-00000.tif', as_attachment=True)

    except Exception as e:
        app.logger.error("Crashed query: /reco/{}.tif: Error: {}".format(dataset_id, e))
        return render_template('error.html', error_message=e)



@app.route('/reco/<int:reco_id>/map.jpg')
def slice_map(reco_id):
    try:
        reco = Reconstruction.query.filter_by(id=reco_id).first()

        map_slice = reco.maps_slices[0]
        return send_from_directory(map_slice.getPathToDir(), "slice_map.jpg")

    except Exception as e:
        app.logger.error("Crashed query: /reco/{}/map.jpg: Error: {}".format(reco_id, e))
        return render_template('error.html', error_message=e)

@app.route('/reco/<int:dataset_id>/slice/<int:number>')
def get_slice(dataset_id, number):
    try:
        dataset = Reconstruction.query.filter_by(id=dataset_id).first()
        path = os.path.abspath(reco_path(dataset))
        return send_from_directory(os.path.join(path, 'slices_thumbs'), 'map-%05i.jpg' % number)

    except Exception as e:
        app.logger.error("Crashed query: /reco/{}/slice/{}: Error: {}".format(dataset_id, number, e))
        return render_template('error.html', error_message=e)

@app.route('/reco/<int:reco_id>/render')
def render(reco_id):
    try:
        reco = Reconstruction.query.filter_by(id=reco_id).first()
        slice_map = SliceMap.query.filter_by(reco_id=reco.id).first()

        slice_map = reco.maps_slices[0]

        return render_template('congote_native_webgl.html', reco=reco, slice_map=slice_map)

    except Exception as e:
        app.logger.error("Crashed query: /reco/{}/render: Error: {}".format(reco_id, e))
        return render_template('error.html', error_message=e)
