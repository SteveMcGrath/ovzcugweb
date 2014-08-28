from app import db
from datetime import datetime, date
from flask.ext.login import UserMixin
from sqlalchemy.ext.hybrid import hybrid_property
from sqlalchemy import desc
import hashlib


def gen_hash(*elements):
    md5 = hashlib.md5()
    for item in elements:
        md5.update(item)
    return md5.hexdigest()


class User(db.Model, UserMixin):
    __tablename__ = 'users'
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(64), unique=True)
    password = db.Column(db.String(32))
    email = db.Column(db.String(255))
    registered_on = db.Column(db.Date, default=date.today())
    admin = db.Column(db.Boolean, default=False)
    machines = db.relationship('Container', backref='owner')

    def __repr__(self):
        return '<USER %s>' % self.username

    def update_password(self, password):
        self.password = gen_hash(password)

    def check_password(self, password):
        return self.password == gen_hash(password)


class Container(db.Model):
    __tablename__ = 'containers'
    id = db.Column(db.Integer, primary_key=True)
    ctid = db.Column(db.Integer)
    node = db.Column(db.String(16))
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'))
    name = db.Column(db.String(255))
    hostname = db.Column(db.String(255))
    ram = db.Column(db.Integer)
    swap = db.Column(db.Integer)
    template = db.Column(db.String(255))
    ipaddresses = db.Column(db.PickleType)

    def __repr__(self):
        return '<Container %s:%s>' % (self.id, self.user_id)

    def start(self):
        return vz.ctl('start', self.node, self.ctid)

    def stop(self):
        return vz.ctl('stop', self.node, self.ctid)

    def restart(self):
        return vz.ctl('restart', self.node, self.ctid)

    def delete(self):
        return vz.ctl('destroy', self.node, self.ctid)

    def create(self):
        return vz.ctl('create', self.node, self.ctid, self.ipaddresses,
                      self.ram, self.swap, self.hostname, self.template)

    def suspend(self):
        return vz.ctl('suspend', self.node, self.ctid)

    def resume(self):
        return vz.ctl('resume', self.node, self.ctid)

    def compact(self):
        return vz.ctl('compact', self.node, self.ctid)

    def migrate(self, destination):
        output = vz.migrate(self.node, destination, self.ctid)
        self.node = destination
        return output
