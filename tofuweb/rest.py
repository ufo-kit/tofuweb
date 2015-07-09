import json
from tofuweb import app, api, models, db
from flask.ext.restful import Resource, reqparse


class Reconstruction(Resource):
    def post(self, dataset_id):
        dataset = db.session.query(models.RawDataset).filter(models.RawDataset.id==dataset_id)
        # print(dataset)
        app.logger.debug(dataset)


api.add_resource(Reconstruction, '/reconstruction/<dataset_id>')
