from tofuweb import db
import os
import os.path

import math

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

class Reconstruction(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    software = db.Column(db.String(128))
    axis = db.Column(db.Float)
    
    done = db.Column(db.Boolean)
    creation_going = db.Column(db.Boolean)
    has_error = db.Column(db.Boolean)

    time = db.Column(db.Float)

    dataset_id = db.Column(db.Integer, db.ForeignKey('dataset.id'))
    dataset = db.relationship('Dataset', backref=db.backref('reconstructions', lazy='dynamic'))

    @property
    def path_to_dir(self):
        return os.path.join('/tmp/recos/', str(self.dataset.id), str(self.id))

    @property
    def slices_number(self):
        return len([name for name in os.listdir(self.path_to_dir) if os.path.isfile( os.path.join(self.path_to_dir,name) )])

    @property
    def path_to_slices(self):
        return os.path.join(self.path_to_dir, 'slice*.tif')

    def __init__(self, dataset, axis=0.0):
        self.dataset = dataset
        self.axis = axis
        self.done = False
        self.creation_going = False
        self.has_error = False

    def __repr__(self):
        return '<Reconstruction id={}, software={}, axis={}, time={}>'.format(self.id, self.software, self.axis, self.time)

class SliceMap(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    done = db.Column(db.Boolean)
    creation_going = db.Column(db.Boolean)
    has_error = db.Column(db.Boolean)
    time = db.Column(db.Float)

    file_name_format = db.Column(db.String)
    
    slices_number = db.Column(db.Integer)
    resize_factor = db.Column(db.Float)
    
    original_slice_width  = db.Column(db.Integer)
    original_slice_height = db.Column(db.Integer)
    
    slice_width  = db.Column(db.Integer)
    slice_height = db.Column(db.Integer)
    
    width  = db.Column(db.Integer)
    height = db.Column(db.Integer)
    
    slices_per_row = db.Column(db.Integer)
    slices_per_col = db.Column(db.Integer)

    slice_maps_numbers = db.Column(db.Integer)
    
    reco_id = db.Column(db.Integer, db.ForeignKey('reconstruction.id'))
    reco = db.relationship('Reconstruction', backref=db.backref('maps_slices', lazy='dynamic'))

    @property
    def path_to_dir(self):
        return os.path.join(self.reco.path_to_dir, "slice_maps")

    def name_of_file(self, index):
        left_part = self.file_name_format.split("%")[0]
        right_part = self.file_name_format.split("%")[1]

        file_name_endings = right_part.split(".")[1]

        file_name_index = "0" + str(index) if index < 10 else str(index)

        file_name = left_part + file_name_index + "." + file_name_endings
        return file_name

    @property
    def volume_size(self):
        return [self.original_slice_width, self.original_slice_height, self.slices_number]


    def __init__(self, reco, file_name_format, row, col, width, height):
        self.reco = reco
        self.done = False
        self.creation_going = False
        self.has_error = False
        self.file_name_format = file_name_format
        
        self.width = width
        self.height = height
        self.slices_per_row = row
        self.slices_per_col = col
        self.slices_number = self.slices_per_row * self.slices_per_col

    def __repr__(self):
        return '<SliceMap path_to_dir={}, slices_number={}, resize_factor={}, original_slice_width={}, original_slice_height={}, slice_width={}, slice_height={}, width={}, height={}, slices_per_row={}, slices_per_col={}, reco_id={}, time={}>'.format(self.path_to_dir, self.slices_number, self.resize_factor, self.original_slice_width, self.original_slice_height, self.slice_width, self.slice_height, self.width, self.height, self.slices_per_row, self.slices_per_col, self.reco_id, self.time)

class SlicesThumbs(db.Model):
    id = db.Column(db.Integer, primary_key=True)

    done = db.Column(db.Boolean)
    creation_going = db.Column(db.Boolean)
    has_error = db.Column(db.Boolean)

    time = db.Column(db.Float)

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
        self.has_error = False

    def __repr__(self):
        return '<SlicesThumbs path_to_dir={}, path_to_thumbs={}, reco_id={}, time={}>'.format(self.path_to_dir, self.path_to_thumbs, self.reco_id, self.time)