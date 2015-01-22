from app import db, vz
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
    registered = db.Column(db.Date, default=date.today())
    admin = db.Column(db.Boolean, default=False)
    expires = db.Column(db.Date, default=date.today())
    membership = db.Column(db.Integer, default=150)
    containers = db.relationship('Container', backref='owner')
    tickets = db.relationship('Ticket', backref='owner')
    payments = db.relationship('Payment', backref='user')

    def __repr__(self):
        return '<USER %s>' % self.username

    @hybrid_property
    def days_left(self):
        return (self.expires - date.today()).days

    @hybrid_property
    def days_member(self):
        return (date.today() - self.registered).days

    @hybrid_property
    def member_status(self):
        if self.days_left >= 30: return 'success'
        elif self.days_left >= 7: return 'warning'
        else: return 'danger'

    def update_password(self, password):
        self.password = gen_hash(password)

    def check_password(self, password):
        return self.password == gen_hash(password)


class Payment(db.Model):
    __tablename__ = 'payments'
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'))
    token = db.Column(db.String(255))
    date = db.Column(db.DateTime, default=datetime.now())

    def __repr__(self):
        return '<PAYMENT %s:%s>' % (self.id, self.user_id)


class Ticket(db.Model):
    __tablename__ = 'tickets'
    id = db.Column(db.Integer, primary_key=True)
    created = db.Column(db.DateTime, default=datetime.now())
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'))
    subject = db.Column(db.String(255))
    priority = db.Column(db.Integer, default=3)
    status = db.Column(db.String(16), default='open')
    text = db.Column(db.Text)
    conversation = db.relationship('Note', backref='ticket')

    @hybrid_property
    def age(self):
        return (datetime.now() - self.created).days

    @hybrid_property
    def priority_text(self):
        data = {0: 'critical', 1: 'high', 2: 'normal', 3: 'low', 4: 'informational'}
        return data[self.priority]

    @hybrid_property
    def priority_class(self):
        data = {0: 'danger', 1: 'warning', 2: 'primary', 3: 'warning', 4: 'default', 5: 'info'}
        return data[self.priority]

    def __repr__(self):
        return '<TICKET %s>' % self.id


class Note(db.Model):
    __tablename__ = 'notes'
    id = db.Column(db.Integer, primary_key=True)
    date = db.Column(db.DateTime, default=datetime.now())
    ticket_id = db.Column(db.Integer, db.ForeignKey('tickets.id'))
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'))
    text = db.Column(db.Text)
    user = db.relationship('User')

    @hybrid_property
    def age(self):
        return (datetime.now() - self.date).days

    def __repr__(self):
        return '<NOTE %s:%s>' % (self.ticket_id, self.id)


class Address(db.Model):
    __tablename__ = 'ipaddresses'
    ip = db.Column(db.String(16), primary_key=True, unique=True)
    container_id = db.Column(db.Integer, default=None)

    def __repr__(self):
        return '<ADDRESS %s>' % self.ip


class Container(db.Model):
    __tablename__ = 'containers'
    id = db.Column(db.Integer, primary_key=True)
    ctid = db.Column(db.Integer)
    node = db.Column(db.String(16))
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'))
    name = db.Column(db.String(255))
    hostname = db.Column(db.String(255))
    disk = db.Column(db.Integer, default=100)
    ram = db.Column(db.Integer, default=1024)
    swap = db.Column(db.Integer, default=1024)
    template = db.Column(db.String(255))
    ipaddresses = db.relationship('Address', backref='container',
                            primaryjoin='Address.container_id==Container.id',
                            foreign_keys='Address.container_id')

    def __repr__(self):
        return '<CONTAINER %s:%s>' % (self.id, self.user_id)

    @hybrid_property
    def info(self):
        return vz.list(self.node, self.ctid)[0]

    def start(self):
        return vz.ctl(self.node, self.ctid, 'start')

    def stop(self):
        return vz.ctl(self.node, self.ctid, 'stop')

    def restart(self):
        return vz.ctl(self.node, self.ctid, 'restart')

    def delete(self):
        return vz.ctl(self.node, self.ctid, 'destroy')

    def create(self):
        vz.ctl(self.node, self.ctid, 'create',
                disk=self.disk,
                ostemplate=self.template
        )
        vz.ctl(self.node, self.ctid, 'set',
                name=self.name, 
                hostname=self.hostname,
                netfilter='full',
                save=''
        )
        for ipaddress in self.ipaddresses:
            vz.ctl('set', self.node, self.ctid, ipadd=ipaddress.ip, save='')
        self.change_ram()

    def suspend(self):
        return vz.ctl(self.node, self.ctid, 'suspend')

    def resume(self):
        return vz.ctl(self.node, self.ctid, 'resume')

    def compact(self):
        return vz.ctl(self.node, self.ctid, 'compact')

    def change_ram(self):
        return vz.ctl(self.node, self.ctid, 'set',
            ram='%dM' % self.ram,
            swap='%dM' % self.disk,
            save=''
        )

    def migrate(self, destination):
        output = vz.migrate(self.node, destination, self.ctid)
        self.node = destination
        return output
