from flask import render_template, flash, redirect, session, url_for, abort, g
from flask.ext.login import login_user, logout_user, current_user, login_required
from app import app, db, login_manager
from app.models import User, Container
from sqlalchemy import desc
from paypal import PayPalConfig
from paypal import PayPalInterface
import forms

#ppconfig = PayPalConfig(
#    API_USERNAME=app.config['PAYPAL_USERNAME'],
#    API_PASSWORD=app.config['PAYPAL_PASSWORD'],
#    API_SIGNATURE=app.config['PAYPAL_SIGNATURE'],
#    DEBUG_LEVEL=0
#)
#ppinterface = PayPalInterface(config=ppconfig)

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
            flash('Invalid Username or Password', 'danger')
    return render_template('login.html', title='Login', form=form)


@app.route('/membership/info')
@app.route('/membership/info/<int:user_id>')
@login_required
def member_info(username=None):
    if username == None:
        username = g.user.username
    user = User.query.filter_by(username=username).first_or_404()
    if g.user.admin or user.id == g.user.id:
        return render_template('userinfo.html', user=user, 
                                title='User Info : %s ' % user.username)
    else:
        flash('Access Denied', 'danger')
        return url_for('vps_list')


@app.route('/logout')
def logout():
    logout_user()
    return redirect(url_for('homepage'))


@app.route('/membership/paypal/pay')
@login_required
def paypal_pay():
    kw = {
        'amt': g.user.membership,
        'currencycode': 'USD',
        'returnurl': url_for('paypal_confirm', _external=True),
        'cancelurl': url_for('paypal_cancel', _external=True),
        'paymentaction': 'Sale',
    }
    ppresp = ppinterface.set_express_checkout(**kw)
    ppurl = ppinterface.generate_express_checkout_redirect_url(ppresp.token)
    return redirect(ppurl)


@app.route('/membership/paypal/cancel')
@login_required
def paypal_cancel():
    return redirect(ur_for('homepage'))


@app.route('/membership/paypal/confirm')
@login_required
def paypal_confirm():
    ppresp = interface.get_express_checkout_details(token=request.args.get('token', ''))
    if ppresp['ACK'] == 'Success':
        ppinterface.do_express_checkout(
            amt=ppresp['AMT'],
            paymentaction='Sale',
            payerid=ppresp['PAYERID'],
            token=ppresp['TOKEN'],
            currencycode=ppresp['CURRENCYCODE']
        )
        checkout = interface.get_express_checkout_details(token=ppresp['TOKEN'])
        if checkout['CHECKOUTSTATUS'] == 'PaymentActionCompleted':
            g.user.payments.append(Payment(token=ppresp['TOKEN']))
            g.user.expires += timedelta(days=365)
            db.session.merge(g.user)
            db.session.commit()
            flash('Payment Applied!  New Expiration is in %s Days' % g.user.days_left, 'success')
        else:
            flash('Payment Unsuccessful.  Paypal says: %s' % checkout['CHECKOUTSTATUS'], 'danger')
    else:
        flash('Error Processing Payment.  Paypal says: %s' % ppresp['ACK'], 'danger')
    return redirect(url_for('member_info'))


@app.route('/tickets')
@login_required
def tickets_list():
    pass


@app.route('/tickets/<int:ticket_id>')
@login_required
def ticket_detail():
    pass


@app.route('/vps/list')
@login_required
def vps_list():
    users = Users.query.all()
    return render_template('vps_list.html', title='VPS List', users=users)


@app.route('/vps/start/<int:vps_id>')
@login_required
def vps_start(vps_id):
    container = Container.query.filter_by(id=vps_id).first_or_404()
    if container.owner == g.user:
        container.start()
        flash('Container Started', 'success')
    return redirect(url_for('vps_list'))


@app.route('/vps/stop/<int:vps_id>')
@login_required
def vps_stop(vps_id):
    container = Container.query.filter_by(id=vps_id).first_or_404()
    if container.owner == g.user:
        container.stop()
        flash('Container Stopped', 'success')
    return redirect(url_for('vps_list'))


@app.route('/vps/restart/<int:vps_id>')
@login_required
def vps_restart(vps_id):
    container = Container.query.filter_by(id=vps_id).first_or_404()
    if container.owner == g.user:
        container.restart()
        flash('Container Started', 'success')
    return redirect(url_for('vps_list'))


@app.route('/vps/compact/<int:vps_id>')
@login_required
def vps_compact(vps_id):
    container = Container.query.filter_by(id=vps_id).first_or_404()
    if container.owner == g.user:
        container.compact()
        flash('Container Compacted', 'success')
    return redirect(url_for('vps_list'))


@app.route('/vps/suspend/<int:vps_id>')
@login_required
def vps_suspend(vps_id):
    container = Container.query.filter_by(id=vps_id).first_or_404()
    if container.owner == g.user:
        container.suspend()
        flash('Container Suspended', 'success')
    return redirect(url_for('vps_list'))


@app.route('/vps/resume/<int:vps_id>')
@login_required
def vps_resume(vps_id):
    container = Container.query.filter_by(id=vps_id).first_or_404()
    if container.owner == g.user:
        container.resume()
        flash('Container Resumed', 'success')
    return redirect(url_for('vps_list'))


@app.route('/vps/update/<int:vps_id>', methods=['GET', 'POST'])
@login_required
def vps_update(vps_id):
    container = Container.query.filter_by(id=vps_id).first_or_404()
    if container.owner == g.user:
        form = forms.HostnameForm()
        if form.validate_on_submit():
            container.update(hostname=form.hostname.data, name=form.name.data)
            flash('Settings Updated', 'success')
        else:
            return render_template('vps_settings.html', 
                title='%s Settings' % container.hostname,
                form=form
            )
    return redirect(url_for('vps_list'))
