import os
from flask.ext.script import Manager
from flask.ext.migrate import MigrateCommand
from tofuweb import app, db
from tofuweb.models import Raw, Reconstruction, Surface


manager = Manager(app)
manager.add_command('db', MigrateCommand)


@manager.command
def createdb():
    db.drop_all()
    db.create_all() 


if __name__ == '__main__':
    manager.run()
