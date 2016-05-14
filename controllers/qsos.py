from flask import Blueprint, render_template, request, redirect, url_for, Response, json, abort, flash
from flask.ext.security import login_required, current_user
from models import db, User, Log, Band
from forms import QsoForm, EditQsoForm
import pytz
import datetime
from libjambon import band_to_frequency, geo_bearing_star
from utils import InvalidUsage, dt_utc_to_user_tz, check_default_profile, get_dxcc_from_clublog
from geohelper import distance, bearing
from libqth import is_valid_qth, qth_to_coords
from calendar import monthrange

bp_qsos = Blueprint('bp_qsos', __name__)


@bp_qsos.route('/logbook/<string:username>', methods=['GET'])
@check_default_profile
def logbook(username):
    user = User.query.filter(User.name == username).first()
    if not user:
        return abort(404)
    try:
        page = int(request.args.get('page', 1))
    except ValueError:
        page = 1

    pcfg = {"title": "{0}'s ({1}) logbook".format(user.name, user.callsign)}

    qsos = Log.query.filter(User.id == user.id).paginate(page=page, per_page=20)

    uqth = user.qth_to_coords()

    d = datetime.datetime.utcnow()
    mr_m = monthrange(d.year, d.month)
    mr_y = monthrange(d.year, 12)

    d_month_start = datetime.datetime(d.year, d.month, 0o1, 00, 00, 00, tzinfo=pytz.timezone('UTC'))
    d_month_end = datetime.datetime(d.year, d.month, mr_m[1], 23, 59, 59, tzinfo=pytz.timezone('UTC'))
    d_year_start = datetime.datetime(d.year, 0o1, 0o1, 00, 00, 00, tzinfo=pytz.timezone('UTC'))
    d_year_end = datetime.datetime(d.year, 12, mr_y[1], 23, 59, 59, tzinfo=pytz.timezone('UTC'))
    cntry_worked = db.session.query(Log.country).filter(Log.user_id == user.id).distinct(Log.country).count()

    stats = {
        'qsos': {
            'total': db.session.query(Log.id).filter(Log.user_id == user.id).count(),
            'month': db.session.query(Log.id).filter(Log.user_id == user.id,
                                                     Log.time_on.between(d_month_start, d_month_end)).count(),
            'year': db.session.query(Log.id).filter(Log.user_id == user.id,
                                                    Log.time_on.between(d_year_start, d_year_end)).count()
        },
        'countries': {
            'worked': cntry_worked,
            'needed': 340 - cntry_worked
        },
        'qsl': {
            'sent': db.session.query(Log.id).filter(Log.user_id == user.id, Log.qsl_sent == 'Y').count(),
            'received': db.session.query(Log.id).filter(Log.user_id == user.id, Log.qsl_rcvd == 'Y').count(),
            'requested': db.session.query(Log.id).filter(Log.user_id == user.id, Log.qsl_sent == 'R').count()
        }
    }

    return render_template('qsos/logbook.jinja2', pcfg=pcfg, qsos=qsos, user=user,
                           uqth=uqth, stats=stats)


@bp_qsos.route('/qsos/new/<string:method>', methods=['GET', 'POST'])
@login_required
@check_default_profile
def new(method):
    if method not in ['live', 'manual']:
        return redirect(url_for('bp_qsos.logbook', user_id=current_user.id))

    pcfg = {"title": "New QSO"}

    form = QsoForm()

    if form.validate_on_submit():
        a = Log()
        # We get from user input a date with timezone offset (we asume that)
        # We store in database in UTC offset, so first convert to DT then makes aware
        # of the user timezone, and then convert to UTC
        date = form.date.data.strftime('%d-%m-%Y')
        time = form.time.data.strftime('%H:%M:%S')
        date_wo_tz = datetime.datetime.strptime("{0} {1}".format(date, time),
                                                "%d-%m-%Y %H:%M:%S")
        date_w_tz = pytz.timezone(current_user.timezone).localize(date_wo_tz)

        a.time_on = date_w_tz.astimezone(pytz.timezone('UTC'))
        a.time_off = date_w_tz.astimezone(pytz.timezone('UTC'))
        a.call = form.call.data
        a.freq = form.freq.data
        a.rst_rcvd = form.rst_rcvd.data
        a.rst_sent = form.rst_sent.data
        a.name = form.name.data
        a.comment = form.comment.data
        a.sat_name = form.sat_name.data
        a.sat_mode = form.sat_mode.data
        a.gridsquare = form.gridsquare.data
        a.country = form.country.data
        a.qsl_sent = form.qsl_sent.raw_data[0]
        a.qsl_sent_via = form.qsl_sent_via.raw_data[0]
        a.qsl_via = form.qsl_via.data
        a.operator = current_user.callsign
        a.owner_callsign = current_user.callsign
        a.station_callsign = current_user.callsign
        a.qth = form.qth.data
        a.prop_mode = form.prop_mode.raw_data[0]
        a.iota = form.iota.data
        a.my_gridsquare = current_user.locator
        a.dxcc = form.dxcc.data
        a.cqz = form.cqz.data
        a.swl = current_user.swl

        a.distance = 0  # ??
        a.freq_rx = 0  # ??

        a.user_id = current_user.id
        a.my_rig = form.radio.raw_data[0]  # TODO relation in model
        a.band_id = form.band.raw_data[0]
        a.mode_id = form.mode.raw_data[0]

        db.session.add(a)
        db.session.commit()
        flash("Success saving QSO with {0} on {1} using {2}".format(
            a.call, a.band.name, a.mode.mode
        ), 'success')
        return redirect(url_for('bp_qsos.new', method=method))

    qsos = Log.query.filter(User.id == current_user.id).limit(16).all()

    return render_template('qsos/new.jinja2', pcfg=pcfg, form=form, logbook=qsos, method=method)


@bp_qsos.route('/qsos/<int:qso_id>/edit', methods=['GET', 'POST'])
@login_required
@check_default_profile
def edit(qso_id):
    pcfg = {"title": "Edit QSO"}

    a = Log.query.get_or_404(qso_id)

    form = EditQsoForm(request.form, a)

    if form.validate_on_submit():
        a.call = form.call.data
        a.freq = form.freq.data
        a.rst_rcvd = form.rst_rcvd.data
        a.rst_sent = form.rst_sent.data
        a.name = form.name.data
        a.comment = form.comment.data
        a.sat_name = form.sat_name.data
        a.sat_mode = form.sat_mode.data
        a.gridsquare = form.gridsquare.data
        a.country = form.country.data
        a.qsl_sent = form.qsl_sent.raw_data[0]
        a.qsl_sent_via = form.qsl_sent_via.raw_data[0]
        a.qsl_via = form.qsl_via.data
        a.operator = current_user.callsign
        a.owner_callsign = current_user.callsign
        a.station_callsign = current_user.callsign
        a.qth = form.qth.data
        a.prop_mode = form.prop_mode.raw_data[0]
        a.iota = form.iota.data
        a.my_gridsquare = current_user.locator
        a.dxcc = form.dxcc.data
        a.cqz = form.cqz.data
        a.swl = current_user.swl

        a.distance = 0  # ??
        a.freq_rx = 0  # ??

        a.user_id = current_user.id
        a.my_rig = form.radio.raw_data[0]  # TODO relation in model
        a.band_id = form.band.raw_data[0]
        a.mode_id = form.mode.raw_data[0]

        a.notes = form.notes.data
        a.qsl_rcvd = form.qsl_rcvd.data
        a.qsl_rcvd_via = form.qsl_rcvd_via.data
        a.eqsl_qsl_rcvd = form.eqsl_qsl_rcvd.data
        a.eqsl_qsl_sent = form.eqsl_qsl_sent.data
        a.lotw_qsl_rcvd = form.lotw_qsl_rcvd.data
        a.lotw_qsl_sent = form.lotw_qsl_sent.data

        db.session.commit()
        flash("Success updating QSO with {0} on {1} using {2}".format(
            a.call, a.band.name, a.mode.mode
        ), 'success')
        return redirect(url_for('bp_qsos.logbook', username=current_user.name))

    # DateTimes in database are stored in UTC format
    # Before displaying them, we convert them to a timezone-aware of UTC
    # Then convert to the current user timezone
    ton_wo_tz = pytz.timezone('UTC').localize(form.time_on.data)
    toff_wo_tz = pytz.timezone('UTC').localize(form.time_off.data)
    form.time_on.data = ton_wo_tz.astimezone(pytz.timezone(current_user.timezone))
    form.time_off.data = toff_wo_tz.astimezone(pytz.timezone(current_user.timezone))

    return render_template('qsos/edit.jinja2', pcfg=pcfg, form=form, log=a)


@bp_qsos.route('/qsos/<int:qso_id>/delete', methods=['GET', 'DELETE', 'PUT'])
@login_required
@check_default_profile
def delete(qso_id):
    qso = Log.query.get_or_404(qso_id)
    db.session.delete(qso)
    db.session.commit()
    return redirect(url_for('bp_qsos.logbook', username=qso.user.name))


@bp_qsos.route('/qsos/lib/jambon/band_to_freq', methods=['GET'])
@login_required
def lib_jambon_band_to_freq():
    band = request.args.get('band')
    mode = request.args.get('mode')

    if not band or not mode:
        raise InvalidUsage('Missing band or mode', status_code=400)

    response = {'status': 'ok', 'band': band, 'mode': mode, 'frequency': band_to_frequency(int(band), int(mode))}
    return Response(json.dumps(response), mimetype='application/json')


@bp_qsos.route('/qsos/lib/geo/bearing', methods=['GET'])
@login_required
def lib_geo_bearing():
    locator_qso = request.args.get('locator_qso')
    locator_user = request.args.get('locator_user')

    if not locator_qso or not locator_user:
        raise InvalidUsage('Missing locator_qso or locator_user', status_code=400)

    if not is_valid_qth(locator_user, 6) or not is_valid_qth(locator_qso, 6):
        raise InvalidUsage('One of the supplied QTH is not valid', status_code=400)

    _f = qth_to_coords(locator_user, 6)  # precision, latitude, longitude
    _t = qth_to_coords(locator_qso, 6)  # precision, latitude, longitude

    response = {'status': 'ok',
                'locator_qso': locator_qso,
                'locator_user': locator_user,
                'distance': distance.haversine_km(_f['latitude'],
                                                  _f['longitude'],
                                                  _t['latitude'],
                                                  _t['longitude']),
                'unit': 'km',
                'bearing': bearing.initial_compass_bearing(_f['latitude'],
                                                           _f['longitude'],
                                                           _t['latitude'],
                                                           _t['longitude'])}
    response['bearing_star'] = geo_bearing_star(response['bearing'])

    return Response(json.dumps(response), mimetype='application/json')


@bp_qsos.route('/qsos/lib/clublog/dxcc', methods=['GET'])
@login_required
def lib_clublog_dxcc():
    callsign = request.args.get('callsign')

    if not callsign:
        raise InvalidUsage('Missing callsign', status_code=400)

    dxcc = get_dxcc_from_clublog(callsign)
    if not dxcc:
        raise InvalidUsage('Error while getting infos from clublog', status_code=500)

    response = {'status': 'ok'}
    response.update(dxcc)

    return Response(json.dumps(response), mimetype='application/json')


@bp_qsos.route('/logbook/<string:username>/geojson', methods=['GET'])
def logbook_geojson(username):
    if not username:
        raise InvalidUsage('Missing username', status_code=400)

    user = User.query.filter(User.name == username).first()
    if not user:
        raise InvalidUsage('User not found', status_code=404)

    logs = Log.query.filter(User.id == user.id).all()

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

    for log in logs:
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
                "name": log.cutename(),
                "callsign": log.call,
                "date": dt_utc_to_user_tz(log.time_on, user=user),
                "band": log.band.name,
                "mode": log.mode.mode,
                "icon": "qso"
            },
            "geometry": {
                "type": "Point",
                "coordinates": [_f['longitude'], _f['latitude']]
            }
        }
        j.append(f)

    return Response(json.dumps(j), mimetype='application/json')


@bp_qsos.route('/logbook/qso/<int:qso_id>/geojson', methods=['GET'])
def logbook_qso_geojson(qso_id):
    if not qso_id:
        raise InvalidUsage('Missing qso_id', status_code=400)

    qso = Log.query.filter(Log.id == qso_id).first()
    if not qso:
        raise InvalidUsage('Qso not found', status_code=404)

    if qso.gridsquare:
        if not is_valid_qth(qso.gridsquare, 6):
            raise InvalidUsage('QTH is not valid', status_code=400)
        _f = qth_to_coords(qso.gridsquare, 6)  # precision, latitude, longitude
    else:
        _f = qso.country_grid_coords()
        if not _f:
            raise InvalidUsage('No valid QTH', status_code=404)

    f = [{
        "type": "Feature",
        "properties": {
            "name": qso.cutename(),
            "callsign": qso.call,
            "date": dt_utc_to_user_tz(qso.time_on, user=qso.user),
            "band": qso.band.name,
            "mode": qso.mode.mode,
            "icon": 'home'
        },
        "geometry": {
            "type": "Point",
            "coordinates": [_f['longitude'], _f['latitude']]
        }
    }]

    if not is_valid_qth(qso.user.locator, 6):
        raise InvalidUsage('QTH is not valid', status_code=400)
    _u = qth_to_coords(qso.user.locator, 6)  # precision, latitude, longitude
    g = {
        "type": "Feature",
        "properties": {
            "name": qso.user.cutename(),
            "callsign": qso.user.callsign,
            "own": True,
            "icon": 'qso'
        },
        "geometry": {
            "type": "Point",
            "coordinates": [_u['longitude'], _u['latitude']]
        }
    }
    f.append(g)

    f.append({
        "type": "LineString",
        "coordinates": [[_f['longitude'], _f['latitude']], [_u['longitude'], _u['latitude']]]
    })

    return Response(json.dumps(f), mimetype='application/json')


@bp_qsos.route('/logbook/qso/<int:qso_id>/modal', methods=['GET'])
def single_qso_modal(qso_id):
    qso = Log.query.get_or_404(qso_id)
    if not qso.gridsquare:
        qso_gs = qso.country_grid()
    else:
        qso_gs = qso.gridsquare

    if not qso_gs or not qso.user.locator:
        raise InvalidUsage('Missing qso.gridsquare or qso.user.locator', status_code=400)

    if not is_valid_qth(qso.user.locator, 6) or not is_valid_qth(qso_gs, 6):
        raise InvalidUsage('One of the supplied QTH is not valid', status_code=400)

    _f = qth_to_coords(qso.user.locator, 6)  # precision, latitude, longitude
    _t = qth_to_coords(qso_gs, 6)  # precision, latitude, longitude

    qso_distance = distance.haversine_km(_f['latitude'],
                                         _f['longitude'],
                                         _t['latitude'],
                                         _t['longitude'])

    qso_bearing = bearing.initial_compass_bearing(_f['latitude'],
                                                  _f['longitude'],
                                                  _t['latitude'],
                                                  _t['longitude'])
    qso_bearing_star = geo_bearing_star(qso_bearing)

    return render_template('qsos/_single_qso_modal.jinja2', qso=qso, qso_distance=qso_distance, qso_bearing=qso_bearing,
                           qso_bearing_star=qso_bearing_star, qso_distance_unit='Km')


@bp_qsos.route('/logbook/stats/<string:username>', methods=['GET'])
@check_default_profile
def logbook_stats(username):
    user = User.query.filter(User.name == username).first()
    if not user:
        return abort(404)
    pcfg = {'title': 'Stats'}

    # Bargraph by year (previous and current)
    stats_months = []
    dt = datetime.datetime.utcnow()

    for y in [dt.year, dt.year - 1]:
        stats_y = []
        for i in range(1, 13):
            mr = monthrange(y, i)
            d_month_start = datetime.datetime(y, i, 0o1, 00, 00, 00, tzinfo=pytz.timezone('UTC'))
            d_month_end = datetime.datetime(y, i, mr[1], 23, 59, 59, tzinfo=pytz.timezone('UTC'))
            stats_y.append([
                i,
                db.session.query(Log.id).filter(Log.user_id == user.id,
                                                Log.time_on.between(d_month_start, d_month_end)).count()
            ])
        stats_months.append(stats_y)

    # Total this year
    total_qso_year = db.session.query(Log.id).filter(Log.user_id == user.id).count()

    # Pie with modes
    stats_modes = []
    modes_used = [{'mode': a.mode.mode, 'id': a.mode.id} for a in
                  Log.query.filter(Log.user_id == user.id).group_by(Log.mode_id).all()]
    for mode in modes_used:
        stats_modes.append({
            'data': db.session.query(Log.id).filter(Log.user_id == user.id, Log.mode_id == mode['id']).count(),
            'label': mode['mode']
        })

    # Pie with bands
    stats_bands = []
    bands_used = [{'band': a.band.name, 'id': a.band.id} for a in
                  Log.query.filter(Log.user_id == user.id).group_by(Log.band_id).all()]
    for band in bands_used:
        stats_bands.append({
            'data': db.session.query(Log.id).filter(Log.user_id == user.id, Log.band_id == band['id']).count(),
            'label': band['band']
        })

    # DXCC Awards worked
    dxcc_bands = ['160m', '80m', '40m', '30m', '20m', '17m', '15m', '12m', '10m', '6m', '4m', '2m', '70cm']
    dxcc_worked = []
    for country in db.session.query(Log.country).filter(Log.user_id == user.id).distinct(Log.country):
        dxcc_entry = {'country': country.country, 'bands': []}
        for band in dxcc_bands:
            band_id = Band.query.filter(Band.name == band,
                                        Band.start.is_(None),
                                        Band.modes.is_(None)).one()
            count = db.session.query(Log.id).filter(Log.user_id == user.id,
                                                    Log.band_id == band_id.id,
                                                    Log.country == country.country).count()
            dxcc_entry['bands'].append({'count': count})
        dxcc_worked.append(dxcc_entry)

    stats = {
        'current_year': stats_months[0],
        'previous_year': stats_months[1],
        'l_cy': dt.year,
        'l_py': dt.year - 1,
        'modes_used': stats_modes,
        'bands_used': stats_bands,
        'total_qsos_year': total_qso_year,
        'bands_list': dxcc_bands,
        'dxcc_worked': dxcc_worked
    }

    return render_template('qsos/stats.jinja2', pcfg=pcfg, stats_json=json.dumps(stats), stats=stats, user=user)
