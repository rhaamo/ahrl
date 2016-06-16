from flask import Blueprint, render_template, request, redirect, url_for, flash, Response, json
from flask_security import login_required, current_user
from models import db, Contact, User, Logbook, Log
from forms import ContactsForm
from utils import check_default_profile, InvalidUsage
from libqth import is_valid_qth, qth_to_coords
from geohelper import distance, bearing
from libjambon import geo_bearing_star
from sqlalchemy import func

bp_contacts = Blueprint('bp_contacts', __name__)


@bp_contacts.route('/contacts', methods=['GET'])
@login_required
@check_default_profile
def contacts():
    pcfg = {"title": "My contacts"}
    _contacts = Contact.query.filter(Contact.user_id == current_user.id).all()
    logbooks = db.session.query(Logbook.id, Logbook.name, func.count(Log.id)).join(
        Log).filter(Logbook.user_id == current_user.id).group_by(Logbook.id).all()
    return render_template('contacts/view.jinja2', pcfg=pcfg, contacts=_contacts, logbooks=logbooks)


@bp_contacts.route('/contacts/<int:contact_id>/edit', methods=['GET', 'POST'])
@login_required
@check_default_profile
def edit(contact_id):
    pcfg = {"title": "Edit my contacts"}
    a = Contact.query.filter(Contact.id == contact_id, Contact.user_id == current_user.id).first()
    if not a:
        flash("Contact not found", "error")
        return redirect(url_for("bp_contacts.contacts"))

    form = ContactsForm(request.form, a)

    if form.validate_on_submit():
        a.callsign = form.callsign.data
        a.gridsquare = form.gridsquare.data

        if not current_user.locator or not form.gridsquare.data:
            flash('Missing locator_qso or locator_user', 'error')
            return redirect(url_for("bp_contacts.contacts"))

        if not is_valid_qth(current_user.locator, 6) or not is_valid_qth(form.gridsquare.data, 6):
            flash('One of the supplied QTH is not valid', 'error')
            return redirect(url_for("bp_contacts.contacts"))

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

    logbooks = db.session.query(Logbook.id, Logbook.name, func.count(Log.id)).join(
        Log).filter(Logbook.user_id == current_user.id).group_by(Logbook.id).all()
    return render_template('contacts/edit.jinja2', pcfg=pcfg, form=form, contact=a,
                           contact_id=contact_id, logbooks=logbooks)


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
            flash('Missing locator_qso or locator_user', 'error')
            return redirect(url_for("bp_contacts.contacts"))

        if not is_valid_qth(current_user.locator, 6) or not is_valid_qth(form.gridsquare.data, 6):
            flash('One of the supplied QTH is not valid', 'error')
            return redirect(url_for("bp_contacts.contacts"))

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

    logbooks = db.session.query(Logbook.id, Logbook.name, func.count(Log.id)).join(
        Log).filter(Logbook.user_id == current_user.id).group_by(Logbook.id).all()
    return render_template('contacts/new.jinja2', pcfg=pcfg, form=form, logbooks=logbooks)


@bp_contacts.route('/contacts/<int:contact_id>/delete', methods=['GET', 'DELETE', 'PUT'])
@login_required
@check_default_profile
def delete(contact_id):
    contact = Contact.query.filter(Contact.id == contact_id, Contact.user_id == current_user.id).first()
    if not contact:
        flash("Contact not found", "error")
        return redirect(url_for("bp_contacts.contacts"))

    db.session.delete(contact)
    db.session.commit()
    flash("Success deleting contact: {0}".format(contact.callsign), 'success')
    return redirect(url_for('bp_contacts.contacts'))


@bp_contacts.route('/contacts/<string:username>/geojson', methods=['GET'])
def contacts_geojson(username):
    if not username:
        raise InvalidUsage('Missing username', status_code=400)

    user = User.query.filter(User.name == username).first()
    if not user:
        raise InvalidUsage('User not found', status_code=404)

    _contacts = Contact.query.filter(User.id == user.id).all()

    if not is_valid_qth(user.locator, 6):
        raise InvalidUsage('QTH is not valid', status_code=400)
    _u = qth_to_coords(user.locator, 6)  # precision, latitude, longitude

    j = [{
        "type": "Feature",
        "properties": {
            "name": user.cutename(),
            "callsign": user.callsign,
            "own": True,
            "icon": "home"
        },
        "geometry": {
            "type": "Point",
            "coordinates": [_u['longitude'], _u['latitude']]
        }
    }]

    for log in _contacts:
        if log.gridsquare:
            if not is_valid_qth(log.gridsquare, 6):
                raise InvalidUsage('QTH is not valid', status_code=400)
            _f = qth_to_coords(log.gridsquare, 6)  # precision, latitude, longitude
        else:
            _f = log.country_grid_coords()
            if not _f:
                continue  # No grid at all ? Skit ip

        f = {
            "type": "Feature",
            "properties": {
                "callsign": log.callsign,
                "distance": log.distance,
                "bearing": log.bearing,
                "bearing_star": log.bearing_star,
                "icon": "qso"
            },
            "geometry": {
                "type": "Point",
                "coordinates": [_f['longitude'], _f['latitude']]
            }
        }
        j.append(f)

    return Response(json.dumps(j), mimetype='application/json')
