from flask import Blueprint, render_template, request, redirect, url_for, flash
from flask.ext.security import login_required, current_user
from models import db, Contact
from forms import ContactsForm
from utils import check_default_profile, InvalidUsage
from libqth import is_valid_qth, qth_to_coords
from geohelper import distance, bearing
from libjambon import geo_bearing_star

bp_contacts = Blueprint('bp_contacts', __name__)


@bp_contacts.route('/contacts', methods=['GET'])
@login_required
@check_default_profile
def contacts():
    pcfg = {"title": "My contacts"}
    _contacts = Contact.query.filter(Contact.user_id == current_user.id).all()
    return render_template('contacts/view.jinja2', pcfg=pcfg, contacts=_contacts)


@bp_contacts.route('/contacts/<int:contact_id>/edit', methods=['GET', 'POST'])
@login_required
@check_default_profile
def edit(contact_id):
    pcfg = {"title": "Edit my contacts"}
    a = Contact.query.get_or_404(contact_id)

    form = ContactsForm(request.form, a)

    if form.validate_on_submit():
        a.callsign = form.callsign.data
        a.gridsquare = form.gridsquare.data

        if not current_user.locator or not form.gridsquare.data:
            raise InvalidUsage('Missing locator_qso or locator_user', status_code=400)

        if not is_valid_qth(current_user.locator, 6) or not is_valid_qth(form.gridsquare.data, 6):
            raise InvalidUsage('One of the supplied QTH is not valid', status_code=400)

        _f = qth_to_coords(current_user.locator, 6)  # precision, latitude, longitude
        _t = qth_to_coords(form.gridsquare.data, 6)  # precision, latitude, longitude

        a.latitude = _t['latitude']
        a.longitude = _t['longitude']
        a.distance = distance.haversine_km(_f['latitude'], _f['longitude'], _t['latitude'], _t['longitude'])
        a.bearing = bearing.initial_compass_bearing(_f['latitude'], _f['longitude'], _t['latitude'], _t['longitude'])
        a.bearing_star = geo_bearing_star(a.bearing)

        db.session.commit()
        flash("Success saving contact: {0}".format(a.callsign), 'success')
        return redirect(url_for('bp_contacts.contacts'))

    return render_template('contacts/edit.jinja2', pcfg=pcfg, form=form, contact=a, contact_id=contact_id)


@bp_contacts.route('/contacts/new', methods=['GET', 'POST'])
@login_required
@check_default_profile
def new():
    pcfg = {"title": "New contact"}

    form = ContactsForm()

    if form.validate_on_submit():
        a = Contact()
        a.callsign = form.callsign.data
        a.gridsquare = form.gridsquare.data

        if not current_user.locator or not form.gridsquare.data:
            raise InvalidUsage('Missing locator_qso or locator_user', status_code=400)

        if not is_valid_qth(current_user.locator, 6) or not is_valid_qth(form.gridsquare.data, 6):
            raise InvalidUsage('One of the supplied QTH is not valid', status_code=400)

        _f = qth_to_coords(current_user.locator, 6)  # precision, latitude, longitude
        _t = qth_to_coords(form.gridsquare.data, 6)  # precision, latitude, longitude

        a.latitude = _t['latitude']
        a.longitude = _t['longitude']
        a.distance = distance.haversine_km(_f['latitude'], _f['longitude'], _t['latitude'], _t['longitude'])
        a.bearing = bearing.initial_compass_bearing(_f['latitude'], _f['longitude'], _t['latitude'], _t['longitude'])
        a.bearing_star = geo_bearing_star(a.bearing)

        a.user_id = current_user.id

        db.session.add(a)
        db.session.commit()
        flash("Success updating contact: {0}".format(a.callsign), 'success')
        return redirect(url_for('bp_contacts.contacts'))

    return render_template('contacts/new.jinja2', pcfg=pcfg, form=form)


@bp_contacts.route('/contacts/<int:contact_id>/delete', methods=['GET', 'DELETE', 'PUT'])
@login_required
@check_default_profile
def delete(contact_id):
    contact = Contact.query.get_or_404(contact_id)
    db.session.delete(contact)
    db.session.commit()
    flash("Success deleting contact: {0}".format(contact.callsign), 'success')
    return redirect(url_for('bp_contacts.contacts'))
