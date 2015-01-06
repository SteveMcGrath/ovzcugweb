from flask import render_template, flash, redirect, session, url_for, abort, g
from flask.ext.login import login_user, logout_user, current_user, login_required
from app import app, db, login_manager, vz
from app.models import User, Container, Ticket, Note, Address, Payment
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
    if g.user.admin:
        tickets = Ticket.query.filter_by(status='open').all()
    else:
        tickets = Ticket.query.filter_by(status='open').filter_by(user_id=g.user.id).all()
    return render_template('ticket_list.html', tickets=tickets)


@app.route('/tickets/detail', methods=['GET', 'POST'])
@app.route('/tickets/detail/<int:ticket_id>', methods=['GET', 'POST'])
@login_required
def ticket_detail(ticket_id=None):
    if ticket_id != None:
        ticket = Ticket.query.filter_by(id=ticket_id).first_or_404()
    else:
        ticket = Ticket()
    if g.user.admin or g.user.id == ticket.user.id:
        update = forms.TicketUpdateForm(obj=ticket)
        notefrm = forms.NewNoteForm()
        if notefrm.validate_on_submit():
            note = Note()
            notefrm.populate_obj(note)
            ticket.notes.append(note)
            db.session.merge(ticket)
            db.session.commit()
            flash('Ticket Updated', 'success')
        if update.validate_on_submit():
            update.populate_obj(ticket)
            db.session.merge(ticket)
            db.session.commit()
            flash('Ticket Status Updated', 'success')
    return render_template('ticket_detail.html', ticket=ticket, update=update, note=notefrm)



@app.route('/user', methods=['GET', 'POST'])
@app.route('/user/<username>', methods=['GET', 'POST'])
def user_edit(username=None):
    if username != None:
        user = User.query.filter_by(username=username).first_or_404()
    else:
        user = User()
    form = forms.NewUserForm(obj=user)
    if form.validate_on_submit():
        if g.user.admin or g.user.username == username:
            form.populate_obj(user)
            if username != None:
                db.session.merge(user)
                flash('User Updated!', 'success')
            else:
                db.session.add(user)
                flash('User Added!', 'success')
            db.session.commit()
        else:
            flash('Access Denied', 'danger')



@app.route('/vps/new/<username>', methods=['GET', 'POST'])
@app.route('/vps/edit/<username>/<int:vps_id>', methods=['GET', 'POST'])
@login_required
def new_vps(username, vps_id=None):
    if g.user.admin:
        user = User.query.filter_by(username=username).first_or_404()
        form = forms.NewContainerForm()
        if form.validate_on_submit():
            vps = Container()
            form.populate_obj(vps)
            vps.name = '%s%s' % (app.config['HOSTNAME_PREFIX'], vps.ipaddresses[0].ip.split('.')[-1])
            vps.hostname = '%s.%s' % (vps.name, app.config['HOSTNAME_SUFFIX'])
            db.session.add(vps)
            db.session.commit()
            vps.ctid = vps.id + 1000
            user.containers.append(vps)
            db.session.merge(user)
            db.session.merge(vps)
            db.session.commit()
            flash('%s Created' % vps.hostname, 'success')
        else:
            return render_template('vps_new.html', form=form)
    else:
        flash('%s is not an admin.' % g.user.username, 'danger')
    return redirect(url_for('vps_list'))


@app.route('/vps/list')
@login_required
def vps_list():
    users = User.query.all()
    vps = {}
    for node in app.config['HARDWARE_NODES']:
        data = vz.list(node, a='')
        for item in data:
            vps[item['ctid']] = item
    return render_template('vps_list.html', title='VPS List', users=users, vps=vps)


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
