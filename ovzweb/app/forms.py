from datetime import date
from flask.ext.wtf import Form
from wtforms.fields import *
from wtforms.ext.sqlalchemy.fields import *
from flask_wtf.html5 import *
from app import app
from wtforms.validators import Required, Optional
from app.models import Address

def available_addresses():
    return Address.query.filter_by(container_id=None)


def hardware_nodes():
    return [(node, node) for node in app.config['HARDWARE_NODES']]


class LoginForm(Form):
    username = TextField('Username', validators=[Required()])
    password = PasswordField('Password', validators=[Required()])
    submit = SubmitField('Submit')


class PasswordForm(Form):
    password = PasswordField('Password', validators=[Required()])
    validate = PasswordField('Validate', validators=[Required()])
    submit = SubmitField('Submit')


class MigrateForm(Form):
    node = SelectField('Hardware Node', validators=[Required()])
    submit = SubmitField('Migrate')


class TemplateForm(Form):
    templates = SelectField('Available Templates', validators=[Required()])
    submit = SubmitField('Create')


class HostnameForm(Form):
    hostname = TextField('Hostname', validators=[Required()])
    name = TextField('Name', validators=[Required()])
    submit = SubmitField('Update')


class NewUserForm(Form):
    username = TextField('Username', validators=[Required()])
    passwd = PasswordField('Password', validators=[Required()])
    pw_verify = PasswordField('Verify Password', validators=[Required()])
    membership = IntegerField('Membership Cost', default=150, validators=[Required()])
    admin = BooleanField('Admin User', default=False)


class NewContainerForm(Form):
    node = SelectField('Hardware Node', choices=hardware_nodes(), validators=[Required()])
    ram = IntegerField('RAM (MB)', default=1024, validators=[Required()])
    swap = IntegerField('Swap (MB)', default=1024, validators=[Required()])
    disk = IntegerField('Disk (GB)', default=100, validators=[Required()])
    ipaddresses = QuerySelectMultipleField('Available IP Addresses', 
        validators=[Required()],
        query_factory=available_addresses, 
        allow_blank=True,
        get_label='ip')


class NewTicketForm(Form):
    subject = TextField('Title', validators=[Required()])
    priority = SelectField('Priority', choices=(
        (5, 'Informational'),
        (4, 'Low'),
        (2, 'Normal'),
        (1, 'High'),
        (0, 'Critical'),
    ), validators=[Required()], default='normal')