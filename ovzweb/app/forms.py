from datetime import date
from flask.ext.wtf import Form
from wtforms.fields import *
from wtforms.validators import Required, Optional


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
    node = SelectField('Hardware Node', validators=[Required()])
    ram = IntegerField('RAM (MB)', default=1024, validators=[Required()])
    swap = IntegerField('Swap (MB)', default=1024, validators=[Required()])
    ipaddr = SelectField('Available IP Addresses', validators=[Required()])


class NewTicketForm(Form):
    subject = TextField('Title', validators=[Required()])
    priority = SelectField('Priority', choices=(
        (5, 'Informational'),
        (4, 'Low'),
        (2, 'Normal'),
        (1, 'High'),
        (0, 'Critical'),
    ), validators=[Required()], default='normal')