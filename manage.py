import os
from flask.ext.script import Manager
from tofuweb import app, db
from tofuweb.models import Raw, Reconstruction


manager = Manager(app)


@manager.command
def createdb():
    db.drop_all()
    db.create_all() 


if __name__ == '__main__':
    manager.run()
