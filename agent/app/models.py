from app import db
from commands import getoutput

class Job(db.Model):
    __tablename__ = 'jobs'
    id = db.Column(db.Integer, primary_key=True)
    command = db.Column(db.Text)
    completed = db.Column(db.Boolean, default=False)
    output = db.Column(db.Text)

    def __init__(self, action, ctid, **opts):
        if action == 'migrate':
            if 'destination' in opts:
                dest = opts['destination']
            else:
                raise Exception('no destination specified')
            self.command = 'vzmigrate -t -c --live %s %s' % (dest, ctid)
        else:
            self.command = 'vzctl %s %s %s' % (action, ctid, ' '.join([
                '--%s %s' % (opt, opts[opt]) for opt in opts
            ]))

    def run(self):
        self.output = getoutput(self.command)
        self.completed = True