from datetime import date
from flask.ext.wtf import Form
from wtforms.fields import *
from wtforms.validators import Required, Optional
from app.models import SubType


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