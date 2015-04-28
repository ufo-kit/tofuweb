from tofuweb import db
import os
from PIL import Image
import math

class MapSliceModel(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    done = db.Column(db.Boolean)
    time = db.Column(db.Float)
    path = db.Column(db.String)

    map_file_name = db.Column(db.String)

    slices_number = db.Column(db.Integer)
    resize_factor = db.Column(db.Float)
    
    original_slice_width  = db.Column(db.Integer)
    original_slice_height = db.Column(db.Integer)
    
    sliceMap_slice_width  = db.Column(db.Integer)
    sliceMap_slice_height = db.Column(db.Integer)
    
    sliceMap_width  = db.Column(db.Integer)
    sliceMap_height = db.Column(db.Integer)
    
    sliceMap_slices_per_row = db.Column(db.Integer)
    sliceMap_slices_per_col = db.Column(db.Integer)
    
    reco_id = db.Column(db.Integer, db.ForeignKey('reconstruction.id'))
    reco = db.relationship('Reconstruction', backref=db.backref('maps_slices', lazy='dynamic'))

    def __init__(self, reco):
        self.reco = reco
        self.done = False
        self.map_file_name = "map_slice.jpg"
        
class Reconstruction(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    software = db.Column(db.String(128))
    axis = db.Column(db.Float)
    done = db.Column(db.Boolean)
    time = db.Column(db.Float)
    path = db.Column(db.String)
    dataset_id = db.Column(db.Integer, db.ForeignKey('dataset.id'))
    dataset = db.relationship('Dataset', backref=db.backref('reconstructions', lazy='dynamic'))

    def __init__(self, dataset, axis=0.0):
        self.dataset = dataset
        self.axis = axis
        self.done = False

    def getPath(self):
        return os.path.join('/tmp/recos/', str(self.dataset.id), str(self.id))

class Dataset(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(128))
    data_path = db.Column(db.String(256))
    flats_path = db.Column(db.String(256), nullable=True)
    darks_path = db.Column(db.String(256), nullable=True)
    projections = db.Column(db.Boolean)

    def __init__(self, name, data, projections=True, darks=None, flats=None):
        self.name = name
        self.data_path = data
        self.darks_path = darks
        self.flats_path = flats
        self.projections = projections

    def __repr__(self):
        return '<DatasetDataset {}>'.format(self.name)
