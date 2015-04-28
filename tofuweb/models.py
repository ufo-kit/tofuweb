from tofuweb import db
import os
from PIL import Image
import math

class SlicesThumbs(db.Model):
    id = db.Column(db.Integer, primary_key=True)

    done = db.Column(db.Boolean)
    creation_going = db.Column(db.Boolean)
    has_error = db.Column(db.Boolean)

    time = db.Column(db.Float)
    
    slices_number = db.Column(db.Integer)
    # path_to_dir = db.Column(db.String)
    # path_to_thumbs = db.Column(db.String)

    reco_id = db.Column(db.Integer, db.ForeignKey('reconstruction.id'))
    reco = db.relationship('Reconstruction', backref=db.backref('slices_thumbs', lazy='dynamic'))
    
    @property
    def path_to_dir(self):
        return os.path.join(self.reco.path_to_dir, "slices_thumbs")
    
    @property
    def path_to_thumbs(self):
        return os.path.join(self.path_to_dir, 'map-%05i.jpg')

    def __init__(self, reco):
        self.reco = reco
        self.done = False
        self.creation_going = False
        self.has_error = True
        # self.path_to_dir = os.path.join(reco.getPathToDir(), "slices_thumbs")
        # self.path_to_thumbs = os.path.join(self.path_to_dir, 'map-%05i.jpg')
    def __repr__(self):
        return '<SlicesThumbs path_to_dir={}, path_to_thumbs={}, reco_id={}, time={}>'.format(self.getPathToDir(), self.getPathToThumbs(), self.reco_id, self.time)

class SliceMap(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    done = db.Column(db.Boolean)
    creation_going = db.Column(db.Boolean)
    has_error = db.Column(db.Boolean)
    time = db.Column(db.Float)

    # path_to_dir = db.Column(db.String)
    # map_file_name = db.Column(db.String)

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

    @property
    def path_to_dir(self):
        return os.path.join(self.reco.path_to_dir, "slice_map")

    def __init__(self, reco):
        self.reco = reco
        self.done = False
        self.creation_going = False
        self.has_error = True
        # self.map_file_name = "slice_map.jpg"
        # self.path_to_dir = os.path.join(reco.getPathToDir(), "slice_map")
        
        self.sliceMap_width = 4096
        self.sliceMap_height = 4096

    def __repr__(self):
        return '<SliceMap path_to_dir={}, slices_number={}, resize_factor={}, original_slice_width={}, original_slice_height={}, sliceMap_slice_width={}, sliceMap_slice_height={}, sliceMap_width={}, sliceMap_height={}, sliceMap_slices_per_row={}, sliceMap_slices_per_col={}, reco_id={}, time={}>'.format(self.getPathToDir(), self.slices_number, self.resize_factor, self.original_slice_width, self.original_slice_height, self.sliceMap_slice_width, self.sliceMap_slice_height, self.sliceMap_width, self.sliceMap_height, self.sliceMap_slices_per_row, self.sliceMap_slices_per_col, self.reco_id, self.time)

class Reconstruction(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    software = db.Column(db.String(128))
    axis = db.Column(db.Float)
    
    done = db.Column(db.Boolean)
    creation_going = db.Column(db.Boolean)
    has_error = db.Column(db.Boolean)

    time = db.Column(db.Float)
    # path_to_dir = db.Column(db.String)
    # path_to_slices = db.Column(db.String)
    dataset_id = db.Column(db.Integer, db.ForeignKey('dataset.id'))
    dataset = db.relationship('Dataset', backref=db.backref('reconstructions', lazy='dynamic'))

    @property
    def path_to_dir(self):
        return os.path.join('/tmp/recos/', str(self.dataset.id), str(self.id))

    @property
    def path_to_slices(self):
        return os.path.join(self.path_to_dir, 'slice*.tif')

    def __init__(self, dataset, axis=0.0):
        self.dataset = dataset
        self.axis = axis
        self.done = False
        self.creation_going = False
        self.has_error = True

    def __repr__(self):
        return '<Reconstruction id={}, software={}, axis={}, time={}>'.format(self.id, self.software, self.axis, self.time)

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