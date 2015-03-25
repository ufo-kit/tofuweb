from tofuweb import db


class Reconstruction(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    software = db.Column(db.String(128))
    axis = db.Column(db.Float)
    done = db.Column(db.Boolean)
    time = db.Column(db.Float)
    dataset_id = db.Column(db.Integer, db.ForeignKey('dataset.id'))
    dataset = db.relationship('Dataset', backref=db.backref('reconstructions', lazy='dynamic'))

    def __init__(self, dataset, axis=0.0):
        self.dataset = dataset
        self.axis = axis
        self.done = False


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
