from flask import render_template, flash, redirect, session, url_for, abort, g
from flask.ext.login import login_user, logout_user, current_user, login_required
from app import app, db, login_manager
from app.models import User, Container
from sqlalchemy import desc
import forms


@login_manager.user_loader
def load_user(userid):
    return User.query.filter_by(id=int(userid)).first()


@app.before_request
def before_request():
    g.user = current_user


@app.route('/')
def homepage():
    return render_template('home.html', title='Home')


@app.route('/membership')
def membership():
    return render_template('membership.html', title='Membership')


@app.route('/about')
def aboutus():
    return render_template('about.html', title='About Us')


@app.route('/login', methods=['GET', 'POST'])
def login():
    if g.user.is_authenticated():
        return redirect(url_for('vps_list'))
    form = forms.LoginForm()
    if form.validate_on_submit():
        user = User.query.filter_by(username=form.username.data).first()
        if user is not None and user.check_password(form.password.data):
            login_user(user)
            return redirect(url_for('vps_list'))
        else:
            user = None
        if user == None:
            flash('Invalid Username or Password', 'error')
    return render_template('login.html', title='Login', form=form)


@app.route('/vps/list')
@login_required
def vps_list():
    return render_template('vps_list.html', title='VPS List')


@app.route('/vps/start/<int:vps_id>')
@login_required
def vps_start(vps_id):
    container = Container.query.filter_by(id=vps_id).first_or_404()
    if container.owner == g.user:
        container.start()
        flash('Container Started')
    return redirect(url_for('vps_list'))


@app.route('/vps/stop/<int:vps_id>')
@login_required
def vps_stop(vps_id):
    container = Container.query.filter_by(id=vps_id).first_or_404()
    if container.owner == g.user:
        container.stop()
        flash('Container Stopped')
    return redirect(url_for('vps_list'))


@app.route('/vps/restart/<int:vps_id>')
@login_required
def vps_restart(vps_id):
    container = Container.query.filter_by(id=vps_id).first_or_404()
    if container.owner == g.user:
        container.restart()
        flash('Container Started')
    return redirect(url_for('vps_list'))


@app.route('/vps/compact/<int:vps_id>')
@login_required
def vps_start(vps_id):
    container = Container.query.filter_by(id=vps_id).first_or_404()
    if container.owner == g.user:
        container.compact()
        flash('Container Compacted')
    return redirect(url_for('vps_list'))


@app.route('/vps/suspend/<int:vps_id>')
@login_required
def vps_suspend(vps_id):
    container = Container.query.filter_by(id=vps_id).first_or_404()
    if container.owner == g.user:
        container.suspend()
        flash('Container Suspended')
    return redirect(url_for('vps_list'))


@app.route('/vps/resume/<int:vps_id>')
@login_required
def vps_resume(vps_id):
    container = Container.query.filter_by(id=vps_id).first_or_404()
    if container.owner == g.user:
        container.resume()
        flash('Container Resumed')
    return redirect(url_for('vps_list'))


@app.route('/vps/update/<int:vps_id>', methods=['GET', 'POST'])
@login_required
def vps_update(vps_id):
    container = Container.query.filter_by(id=vps_id).first_or_404()
    if container.owner == g.user:
        form = forms.HostnameForm()
        if form.validate_on_submit():
            container.update(hostname=form.hostname.data, name=form.name.data)
            flash('Settings Updated')
        else:
            return render_template('vps_settings.html', 
                title='%s Settings' % container.hostname,
                form=form
            )
    return redirect(url_for('vps_list'))
