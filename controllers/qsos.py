import datetime
import os
from calendar import monthrange
from libqth import is_valid_qth, qth_to_coords

import pytz
from flask import Blueprint, render_template, request, redirect, url_for, Response, json, flash, current_app
from flask_security import login_required, current_user
from flask_uploads import UploadSet, IMAGES
from geohelper import distance, bearing
from sqlalchemy import func
from sqlalchemy.orm import Bundle
from sqlalchemy.sql.expression import case

from forms import QsoForm, EditQsoForm, FilterLogbookBandMode, PictureForm, AdvSearchForm
from libjambon import band_to_frequency, geo_bearing_star, get_dxcc_from_clublog_or_database
from models import db, User, Log, Band, Mode, Logbook, Picture
from models import ham_country_grid_coords, cutename
from utils import InvalidUsage, dt_utc_to_user_tz, check_default_profile

from pyhamqth import HamQTH, HamQTHQueryFailed

bp_qsos = Blueprint("bp_qsos", __name__)

pictures = UploadSet("pictures", IMAGES)


@bp_qsos.route("/user/<string:username>/logbook/<string:logbook_slug>", methods=["GET"])
@check_default_profile
def logbook(username, logbook_slug):
    user = User.query.filter(User.name == username).first()
    if not user:
        flash("User not found", "error")
        return redirect(url_for("bp_main.home"))

    try:
        page = int(request.args.get("page", 1))
    except ValueError:
        page = 1

    pcfg = {"title": "{0}'s ({1}) logbook".format(user.name, user.callsign)}

    _logbook = Logbook.query.filter(Logbook.slug == logbook_slug, Logbook.user_id == user.id).first()
    if not _logbook:
        flash("Logbook not found", "error")
        return redirect(url_for("bp_logbooks.logbooks", user=user.name))

    if not _logbook.public and not current_user.is_authenticated:
        flash("Logbook not found", "error")
        return redirect(url_for("bp_logbooks.logbooks", user=user.name))

    if not _logbook.public and _logbook.user_id != current_user.id:
        flash("Logbook not found", "error")
        return redirect(url_for("bp_logbooks.logbooks", user=user.name))

    if is_valid_qth(user.locator, 6):
        uqth = user.qth_to_coords()
    else:
        flash("User gridsquare is invalid")
        return redirect(url_for("bp_logbooks.logbooks", user=user.name))

    d = datetime.datetime.utcnow()
    mr_m = monthrange(d.year, d.month)
    mr_y = monthrange(d.year, 12)

    d_month_start = datetime.datetime(d.year, d.month, 0o1, 00, 00, 00, tzinfo=pytz.timezone("UTC"))
    d_month_end = datetime.datetime(d.year, d.month, mr_m[1], 23, 59, 59, tzinfo=pytz.timezone("UTC"))
    d_year_start = datetime.datetime(d.year, 0o1, 0o1, 00, 00, 00, tzinfo=pytz.timezone("UTC"))
    d_year_end = datetime.datetime(d.year, 12, mr_y[1], 23, 59, 59, tzinfo=pytz.timezone("UTC"))
    cntry_worked = (
        db.session.query(Log.country)
        .filter(Log.user_id == user.id, Log.logbook_id == _logbook.id)
        .distinct(Log.country)
        .count()
    )

    # Form filter display thing and QSOs filtering
    filter_form = FilterLogbookBandMode()
    q_mode = None
    q_band = None
    rq_mode = request.args.get("mode", None)
    rq_band = request.args.get("band", None)

    if rq_mode or rq_mode != "all":
        q_mode = Mode.query.filter(Mode.submode == rq_mode)
        if q_mode.count() == 1:
            q_mode = q_mode.first()
        else:
            q_mode = None
    if rq_band or rq_band != "all":
        q_band = Band.query.filter(Band.modes.is_(None), Band.start.is_(None), Band.name == rq_band)
        if q_band.count() == 1:
            q_band = q_band.first()
        else:
            q_band = None

    # Form choices building
    filter_modes = []
    _a_logs = Bundle("log", Log.mode_id)
    _b_modes = Bundle("modes", Mode.id, Mode.mode, Mode.submode)
    for _modes, _logs in (
        db.session.query(_b_modes, _a_logs)
        .join(Mode.logs)
        .filter(Log.user_id == user.id, Log.logbook_id == _logbook.id)
        .group_by(_a_logs, _b_modes)
        .all()
    ):
        filter_modes.append([_modes.id, "{0} - {1}".format(_modes.mode, _modes.submode)])

    filter_bands = []
    _a_logs = Bundle("log", Log.band_id)
    _b_bands = Bundle("bands", Band.id, Band.name)
    for _bands, _logs in (
        db.session.query(_b_bands, _a_logs)
        .join(Band.logs)
        .filter(Log.user_id == user.id, Log.logbook_id == _logbook.id)
        .group_by(_a_logs, _b_bands)
        .all()
    ):
        filter_bands.append([_bands.name, _bands.name])

    filter_modes.insert(0, ["all", "All modes"])
    filter_bands.insert(0, ["all", "All bands"])

    filter_form.mode.choices = filter_modes
    filter_form.mode.data = rq_mode or "all"
    filter_form.band.choices = filter_bands
    filter_form.band.data = rq_band or "all"

    bq = Log.query.filter(User.id == user.id, Log.logbook_id == _logbook.id)

    if q_mode and not q_band:
        fquery = bq.filter(Log.mode_id == q_mode.id)
    elif not q_mode and q_band:
        fquery = bq.filter(Log.band_id == q_band.id)
    elif q_mode and q_band:
        fquery = bq.filter(Log.mode_id == q_mode.id, Log.band_id == q_band.id)
    else:
        fquery = bq

    qsos = fquery.paginate(page=page, per_page=20)

    # Column of stats
    stats = {
        "qsos": {
            "total": db.session.query(Log.id).filter(Log.user_id == user.id, Log.logbook_id == _logbook.id).count(),
            "month": db.session.query(Log.id)
            .filter(
                Log.user_id == user.id, Log.time_on.between(d_month_start, d_month_end), Log.logbook_id == _logbook.id
            )
            .count(),
            "year": db.session.query(Log.id)
            .filter(
                Log.user_id == user.id, Log.time_on.between(d_year_start, d_year_end), Log.logbook_id == _logbook.id
            )
            .count(),
        },
        "countries": {"worked": cntry_worked, "needed": 340 - cntry_worked},
        "qsl": {
            "sent": db.session.query(Log.id)
            .filter(Log.user_id == user.id, Log.qsl_sent == "Y", Log.logbook_id == _logbook.id)
            .count(),
            "received": db.session.query(Log.id)
            .filter(Log.user_id == user.id, Log.qsl_rcvd == "Y", Log.logbook_id == _logbook.id)
            .count(),
            "requested": db.session.query(Log.id)
            .filter(Log.user_id == user.id, Log.qsl_sent == "R", Log.logbook_id == _logbook.id)
            .count(),
        },
    }

    if current_user.is_authenticated:
        logbooks = (
            db.session.query(Logbook.id, Logbook.slug, Logbook.name, func.count(Log.id))
            .join(Log)
            .filter(Logbook.user_id == current_user.id)
            .group_by(Logbook.id)
            .all()
        )
    else:
        logbooks = (
            db.session.query(Logbook.id, Logbook.slug, Logbook.name, func.count(Log.id))
            .join(Log)
            .filter(Logbook.user_id == user.id, Logbook.public.is_(True))
            .group_by(Logbook.id)
            .all()
        )

    return render_template(
        "qsos/logbook.jinja2",
        pcfg=pcfg,
        qsos=qsos,
        user=user,
        logbook=_logbook,
        uqth=uqth,
        stats=stats,
        filter_form=filter_form,
        band=rq_band,
        mode=rq_mode,
        logbooks=logbooks,
    )


@bp_qsos.route("/logbook/<string:logbook_slug>/qsos/new/<string:method>", methods=["GET", "POST"])
@login_required
@check_default_profile
def new(logbook_slug, method):
    if method not in ["live", "manual"]:
        return redirect(url_for("bp_qsos.logbook", user_id=current_user.id))

    pcfg = {"title": "New QSO"}

    form = QsoForm()

    _logbook = Logbook.query.filter(Logbook.slug == logbook_slug, Logbook.user_id == current_user.id).first()
    if not _logbook or _logbook.user_id != current_user.id:
        flash("Logbook not found !", "error")
        return redirect(url_for("bp_logbooks.logbooks", user=current_user.name))

    logbooks = (
        db.session.query(Logbook.id, Logbook.slug, Logbook.name, func.count(Log.id))
        .join(Log)
        .filter(Logbook.user_id == current_user.id)
        .group_by(Logbook.id)
        .all()
    )

    if form.validate_on_submit():
        a = Log()
        # We get from user input a date with timezone offset (we asume that)
        # We store in database in UTC offset, so first convert to DT then makes aware
        # of the user timezone, and then convert to UTC
        date = form.date.data.strftime("%Y-%m-%d")
        time = form.time.data.strftime("%H:%M:%S")
        date_wo_tz = datetime.datetime.strptime("{0} {1}".format(date, time), "%Y-%m-%d %H:%M:%S")
        date_w_tz = pytz.timezone(current_user.timezone).localize(date_wo_tz)

        a.time_on = date_w_tz.astimezone(pytz.timezone("UTC")).replace(tzinfo=None)
        a.time_off = date_w_tz.astimezone(pytz.timezone("UTC")).replace(tzinfo=None)

        a.call = form.call.data.upper()
        a.freq = form.freq.data
        a.rst_rcvd = form.rst_rcvd.data
        a.rst_sent = form.rst_sent.data
        a.name = form.name.data
        a.comment = form.comment.data
        a.qsl_comment = form.qsl_comment.data
        a.sat_name = form.sat_name.data.upper()
        a.sat_mode = form.sat_mode.data.upper()

        if not form.gridsquare.data or form.gridsquare.data == "":
            cmp_qth = ham_country_grid_coords(a.call)
            if cmp_qth and "qth" in cmp_qth:
                a.cache_gridsquare = cmp_qth["qth"]
        else:
            a.gridsquare = form.gridsquare.data.upper()
            a.cache_gridsquare = a.gridsquare

        a.country = form.country.data
        a.qsl_sent = form.qsl_sent.raw_data[0]
        a.qsl_sent_via = form.qsl_sent_via.raw_data[0]
        a.qsl_via = form.qsl_via.data
        a.eqsl_qsl_sent = form.eqsl_qsl_sent.data
        a.operator = current_user.callsign.upper()
        a.owner_callsign = current_user.callsign.upper()
        a.station_callsign = current_user.callsign.upper()
        a.qth = form.qth.data
        a.prop_mode = form.prop_mode.raw_data[0]
        a.iota = form.iota.data.upper()
        a.my_gridsquare = current_user.locator.upper()
        a.dxcc = form.dxcc.data
        a.cqz = form.cqz.data
        a.swl = 1 if _logbook.swl else 0
        a.web = form.web.data

        a.distance = 0  # ??
        a.freq_rx = 0  # ??

        a.user_id = current_user.id
        a.my_rig = form.radio.raw_data[0]  # TODO relation in model
        a.band_id = form.band.raw_data[0]
        a.mode_id = form.mode.raw_data[0]

        a.logbook_id = _logbook.id

        db.session.add(a)
        db.session.commit()
        flash("Success saving QSO with {0} on {1} using {2}".format(a.call, a.band.name, a.mode.submode), "success")
        return redirect(url_for("bp_qsos.new", method=method, logbook_slug=_logbook.slug))

    return render_template("qsos/new.jinja2", pcfg=pcfg, form=form, method=method, logbook=_logbook, logbooks=logbooks)


@bp_qsos.route("/logbook/<string:logbook_slug>/qsos/<string:qso_slug>/edit", methods=["GET", "POST"])
@login_required
@check_default_profile
def edit(logbook_slug, qso_slug):
    pcfg = {"title": "Edit QSO"}

    _logbook = Logbook.query.filter(Logbook.slug == logbook_slug, Logbook.user_id == current_user.id).first()
    if not _logbook or _logbook.user_id != current_user.id:
        flash("Logbook not found !", "error")
        return redirect(url_for("bp_logbooks.logbooks", user=current_user.name))

    a = Log.query.filter(Log.slug == qso_slug, Log.user_id == current_user.id, Log.logbook_id == _logbook.id).first()
    if not a:
        flash("Qso not found", "error")
        return redirect(url_for("bp_logbooks.logbooks", user=current_user.name))

    logbooks = (
        db.session.query(Logbook.id, Logbook.slug, Logbook.name, func.count(Log.id))
        .join(Log)
        .filter(Logbook.user_id == current_user.id)
        .group_by(Logbook.id)
        .all()
    )

    form = EditQsoForm(request.form, obj=a)

    # Fix bug with SelectField not managing relations properly
    form.mode.data = a.mode.id

    if form.validate_on_submit():
        a.call = form.call.data.upper()
        a.freq = form.freq.data
        a.rst_rcvd = form.rst_rcvd.data
        a.rst_sent = form.rst_sent.data
        a.name = form.name.data
        a.comment = form.comment.data
        a.qsl_comment = form.qsl_comment.data
        a.sat_name = form.sat_name.data.upper()
        a.sat_mode = form.sat_mode.data.upper()

        if not form.gridsquare.data or form.gridsquare.data == "":
            cmp_qth = ham_country_grid_coords(a.call)
            if not cmp_qth:
                flash("Could not find Grid Square", "error")
                # return redirect(url_for("bp_logbooks.logbooks", user=current_user.name))
            if cmp_qth:
                a.cache_gridsquare = cmp_qth["qth"]
            a.gridsquare = form.gridsquare.data.upper()
        else:
            a.gridsquare = form.gridsquare.data.upper()
            a.cache_gridsquare = a.gridsquare

        a.country = form.country.data
        a.qsl_sent = form.qsl_sent.raw_data[0]
        a.qsl_sent_via = form.qsl_sent_via.raw_data[0]
        a.qsl_via = form.qsl_via.data
        a.qth = form.qth.data
        a.prop_mode = form.prop_mode.raw_data[0]
        a.iota = form.iota.data.upper()
        a.dxcc = form.dxcc.data
        a.cqz = form.cqz.data
        a.web = form.web.data

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

        ton_as_usr = pytz.timezone(current_user.timezone).localize(form.time_on.data)
        toff_as_usr = pytz.timezone(current_user.timezone).localize(form.time_off.data)

        ton_as_utc = ton_as_usr.astimezone(pytz.timezone("UTC"))
        toff_as_utc = toff_as_usr.astimezone(pytz.timezone("UTC"))
        a.time_on = ton_as_utc
        a.time_off = toff_as_utc

        db.session.commit()
        flash("Success updating QSO with {0} on {1} using {2}".format(a.call, a.band.name, a.mode.submode), "success")
        return redirect(url_for("bp_qsos.logbook", username=current_user.name, logbook_slug=a.logbook.slug))

    # DateTimes in database are stored in UTC format
    # Before displaying them, we convert them to a timezone-aware of UTC
    # Then convert to the current user timezone
    ton_wo_tz = pytz.timezone("UTC").localize(form.time_on.data)
    toff_wo_tz = pytz.timezone("UTC").localize(form.time_off.data)
    form.time_on.data = ton_wo_tz.astimezone(pytz.timezone(current_user.timezone)).replace(tzinfo=None)
    form.time_off.data = toff_wo_tz.astimezone(pytz.timezone(current_user.timezone)).replace(tzinfo=None)

    return render_template("qsos/edit.jinja2", pcfg=pcfg, form=form, log=a, logbook=a.logbook, logbooks=logbooks)


@bp_qsos.route("/qsos/<string:qso_slug>/delete", methods=["GET", "DELETE", "PUT"])
@login_required
@check_default_profile
def delete(qso_slug):
    qso = Log.query.filter(Log.user_id == current_user.id, Log.slug == qso_slug).first()
    if not qso or qso.user_id != current_user.id:
        flash("Qso not found", "error")
        return redirect(url_for("bp_logbooks.logbooks", user=current_user.name))

    logbook_slug = qso.logbook.slug
    db.session.delete(qso)
    db.session.commit()
    return redirect(url_for("bp_qsos.logbook", username=qso.user.name, logbook_slug=logbook_slug))


@bp_qsos.route("/qsos/lib/jambon/band_to_freq", methods=["GET"])
@login_required
def lib_jambon_band_to_freq():
    band = request.args.get("band")
    mode = request.args.get("mode")

    if not band or not mode:
        raise InvalidUsage("Missing band or mode", status_code=400)

    response = {"status": "ok", "band": band, "mode": mode, "frequency": band_to_frequency(int(band), int(mode))}
    return Response(
        json.dumps(response, encoding="utf-8", ensure_ascii=False), mimetype="application/json;charset=utf-8"
    )


@bp_qsos.route("/qsos/lib/geo/bearing", methods=["GET"])
@login_required
def lib_geo_bearing():
    locator_qso = request.args.get("locator_qso")
    locator_user = request.args.get("locator_user")

    if not locator_qso or not locator_user:
        raise InvalidUsage("Missing locator_qso or locator_user", status_code=400)

    if not is_valid_qth(locator_user, 6) or not is_valid_qth(locator_qso, 6):
        raise InvalidUsage("One of the supplied QTH is not valid", status_code=400)

    _f = qth_to_coords(locator_user, 6)  # precision, latitude, longitude
    _t = qth_to_coords(locator_qso, 6)  # precision, latitude, longitude

    response = {
        "status": "ok",
        "locator_qso": locator_qso,
        "locator_user": locator_user,
        "distance": distance.haversine_km(_f["latitude"], _f["longitude"], _t["latitude"], _t["longitude"]),
        "unit": "km",
        "bearing": bearing.initial_compass_bearing(_f["latitude"], _f["longitude"], _t["latitude"], _t["longitude"]),
    }
    response["bearing_star"] = geo_bearing_star(response["bearing"])

    return Response(
        json.dumps(response, encoding="utf-8", ensure_ascii=False), mimetype="application/json;charset=utf-8"
    )


@bp_qsos.route("/qsos/lib/clublog/dxcc", methods=["GET"])
@login_required
def lib_clublog_dxcc():
    callsign = request.args.get("callsign")
    if not callsign:
        raise InvalidUsage("Missing callsign", status_code=400)

    dxcc = get_dxcc_from_clublog_or_database(callsign.upper())
    if not dxcc:
        # We have nothing at all :(
        raise InvalidUsage("Error while getting infos from clublog or database", status_code=500)

    response = {"status": "ok"}
    response.update(dxcc)

    return Response(
        json.dumps(response, encoding="utf-8", ensure_ascii=False), mimetype="application/json;charset=utf-8"
    )


@bp_qsos.route("/qsos/lib/hamqth/call", methods=["GET"])
@login_required
def lib_hamqth_call():
    callsign = request.args.get("callsign")
    if not callsign:
        raise InvalidUsage("Missing callsign", status_code=400)

    if not current_user.hamqth_name or not current_user.hamqth_password:
        raise InvalidUsage("Missing HamQTH Username or Password", status_code=500)

    _v = "AHRL"
    _hq = HamQTH(user=current_user.hamqth_name, password=current_user.hamqth_password, user_agent_suffix=_v)
    _csd = None

    try:
        _csd = _hq.lookup_callsign_data(callsign)
    except HamQTHQueryFailed as e:
        if str(e) != "Got error from API: Callsign not found":
            raise InvalidUsage("API Error: {0}".format(e), status_code=400)

    response = {"status": "ok"}
    if _csd:
        response.update(_csd)

    return Response(
        json.dumps(response, encoding="utf-8", ensure_ascii=False), mimetype="application/json;charset=utf-8"
    )


@bp_qsos.route("/user/<string:username>/logbook/<string:logbook_slug>/geojson", methods=["GET"])
def logbook_geojson(username, logbook_slug):
    if not username:
        raise InvalidUsage("Missing username", status_code=400)

    user = User.query.filter(User.name == username).first()
    if not user:
        raise InvalidUsage("User not found", status_code=404)

    _logbook = Logbook.query.filter(Logbook.slug == logbook_slug, Logbook.user_id == user.id).first()
    if not _logbook:
        raise InvalidUsage("Logbook not found", status_code=404)

    if not _logbook.public and not current_user.is_authenticated:
        raise InvalidUsage("Logbook not found", status_code=404)

    if _logbook.user_id != user.id:
        raise InvalidUsage("Logbook not found", status_code=404)

    if not _logbook.public and _logbook.user_id != current_user.id:
        raise InvalidUsage("Logbook not found", status_code=404)

    # QSO filter thing
    q_mode = None
    q_band = None
    rq_mode = request.args.get("mode", None)
    rq_band = request.args.get("band", None)

    if rq_mode or rq_mode != "all":
        q_mode = Mode.query.filter(Mode.mode == rq_mode).first()
    if rq_band or rq_band != "all":
        q_band = Band.query.filter(Band.modes.is_(None), Band.start.is_(None), Band.name == rq_band).first()

    # Log.id, Log.gridsquare, Log.call, Log.time_on, Log.band.name, Log.mode.mode, Log.mode.submode, Log.band.name
    # .. country, qth
    xpr = case([(Log.gridsquare != "", Log.gridsquare)], else_=Log.cache_gridsquare)
    bq = (
        db.session.query(Log.id, xpr, Log.call, Log.time_on, Band.name, Mode.mode, Mode.submode, Log.country, Log.qth)
        .join(Band)
        .join(Mode)
        .filter(Log.user_id == user.id, Log.logbook_id == _logbook.id)
    )

    if q_mode and not q_band:
        fquery = bq.filter(Log.mode_id == q_mode.id)
    elif not q_mode and q_band:
        fquery = bq.filter(Log.band_id == q_band.id)
    elif q_mode and q_band:
        fquery = bq.filter(Log.mode_id == q_mode.id, Log.band_id == q_band.id)
    else:
        fquery = bq

    logs = fquery.all()

    if not is_valid_qth(user.locator, 6):
        raise InvalidUsage("QTH is not valid", status_code=400)
    _u = qth_to_coords(user.locator, 6)  # precision, latitude, longitude

    j = [
        {
            "type": "Feature",
            "properties": {"name": user.cutename(), "callsign": user.callsign, "own": True, "icon": "home"},
            "geometry": {"type": "Point", "coordinates": [_u["longitude"], _u["latitude"]]},
        }
    ]

    qsos = {}
    # First dict, one key per call, with a list of all QSOs, etc.
    for log in logs:
        # (0, None, 'EA3EW0', datetime.datetime(2016, 6, 10, 19, 53, 29), 'SSTV', 'SSTV', '4mm', 'country', 'qth')
        if log[1]:
            if not is_valid_qth(log[1], 6):
                raise InvalidUsage("QTH is not valid", status_code=400)
            _f = qth_to_coords(log[1], 6)  # precision, latitude, longitude
        else:
            continue  # No grid at all ? Skit ip

        if not log[2] in qsos:
            qsos[log[2]] = {
                "call": cutename(log.call),
                "coordinates": [_f["longitude"], _f["latitude"]],
                "qsos": [],
                "country": log.country,
                "qth": log.qth,
            }

        qsos[log[2]]["qsos"].append(
            {
                "date": dt_utc_to_user_tz(log.time_on, user=user),
                "band": log.name,
                "mode": log.mode,
                "submode": log.submode,
            }
        )

    # Second dict, transform to GeoJSON
    for qso in qsos.keys():
        f = {
            "type": "Feature",
            "properties": {
                "name": qsos[qso]["call"],
                "callsign": qsos[qso]["call"],
                "qsos": qsos[qso]["qsos"],
                "country": qsos[qso]["country"],
                "qth": qsos[qso]["qth"],
                "icon": "qso",
            },
            "geometry": {"type": "Point", "coordinates": qsos[qso]["coordinates"]},
        }
        j.append(f)

    return Response(json.dumps(j, encoding="utf-8", ensure_ascii=False), mimetype="application/json;charset=utf-8")


@bp_qsos.route("/logbook/qso/<int:qso_id>/geojson", methods=["GET"])
def logbook_qso_geojson(qso_id):
    if not qso_id:
        raise InvalidUsage("Missing qso_id", status_code=400)

    qso = Log.query.filter(Log.id == qso_id).first()
    if not qso:
        raise InvalidUsage("Qso not found", status_code=404)

    if not qso.logbook.public and not current_user.is_authenticated:
        raise InvalidUsage("Qso not found", status_code=404)

    if not qso.logbook.public and qso.logbook.user_id != current_user.id:
        raise InvalidUsage("Qso not found", status_code=404)

    if qso.gridsquare:
        if not is_valid_qth(qso.gridsquare, 6):
            raise InvalidUsage("QTH is not valid", status_code=400)
        _f = qth_to_coords(qso.gridsquare, 6)  # precision, latitude, longitude
    else:
        _f = qso.country_grid_coords()
        if not _f:
            raise InvalidUsage("No valid QTH", status_code=404)

    f = [
        {
            "type": "Feature",
            "properties": {
                "name": qso.cutename(),
                "callsign": qso.call,
                "date": dt_utc_to_user_tz(qso.time_on, user=qso.user),
                "band": qso.band.name,
                "mode": qso.mode.mode,
                "submode": qso.mode.submode,
                "icon": "qso",
            },
            "geometry": {"type": "Point", "coordinates": [_f["longitude"], _f["latitude"]]},
        }
    ]

    if not is_valid_qth(qso.user.locator, 6):
        raise InvalidUsage("QTH is not valid", status_code=400)
    _u = qth_to_coords(qso.user.locator, 6)  # precision, latitude, longitude
    g = {
        "type": "Feature",
        "properties": {"name": qso.user.cutename(), "callsign": qso.user.callsign, "own": True, "icon": "home"},
        "geometry": {"type": "Point", "coordinates": [_u["longitude"], _u["latitude"]]},
    }
    f.append(g)

    f.append(
        {"type": "LineString", "coordinates": [[_f["longitude"], _f["latitude"]], [_u["longitude"], _u["latitude"]]]}
    )

    return Response(json.dumps(f, encoding="utf-8", ensure_ascii=False), mimetype="application/json;charset=utf-8")


@bp_qsos.route("/user/<string:username>/logbook/<string:logbook_slug>/qso/<string:qso_slug>", methods=["GET"])
@bp_qsos.route(
    "/user/<string:username>/logbook/<string:logbook_slug>/qso/<string:qso_slug>/pictures/new",
    endpoint="view_post",
    methods=["POST"],
)
@check_default_profile
def view(username, logbook_slug, qso_slug):
    user = User.query.filter(User.name == username).first()
    if not user:
        flash("User not found", "error")
        return redirect(url_for("bp_main.home"))

    _logbook = Logbook.query.filter(Logbook.slug == logbook_slug, Logbook.user_id == user.id).first()
    if not _logbook:
        flash("Logbook not found", "error")
        return redirect(url_for("bp_logbooks.logbooks", user=user.name))

    qso = Log.query.filter(Log.slug == qso_slug, Log.user_id == user.id).first()
    if not qso:
        flash("Qso not found", "error")
        return redirect(url_for("bp_qsos.logbook", username=user.name, logbook_slug=_logbook.slug))

    if qso.logbook != _logbook:
        flash("Qso not found", "error")
        return redirect(url_for("bp_qsos.logbook", username=user.name, logbook_slug=_logbook.slug))

    if not qso.logbook.public and not current_user.is_authenticated:
        flash("Qso not found", "error")
        return redirect(url_for("bp_qsos.logbook", username=user.name, logbook_slug=_logbook.slug))

    if not qso.logbook.public and qso.user_id != current_user.id:
        flash("Qso not found", "error")
        return redirect(url_for("bp_qsos.logbook", username=user.name, logbook_slug=_logbook.slug))

    pcfg = {"title": "View QSO with {0}".format(qso.call)}

    if not qso.gridsquare:
        qso_gs = qso.country_grid()
    else:
        qso_gs = qso.gridsquare

    if not is_valid_qth(qso.user.locator, 6):
        flash("User supplied QTH is not valid")
        return redirect(url_for("bp_qsos.logbook", username=user.name, logbook_slug=_logbook.slug))

    if qso_gs and not is_valid_qth(qso_gs, 6):
        flash("QSO supplied QTH is not valid")
        return redirect(url_for("bp_qsos.logbook", username=user.name, logbook_slug=_logbook.slug))

    if qso_gs and qso.user.locator:
        _f = qth_to_coords(qso.user.locator, 6)  # precision, latitude, longitude
        _t = qth_to_coords(qso_gs, 6)  # precision, latitude, longitude

        qso_distance = distance.haversine_km(_f["latitude"], _f["longitude"], _t["latitude"], _t["longitude"])

        qso_bearing = bearing.initial_compass_bearing(_f["latitude"], _f["longitude"], _t["latitude"], _t["longitude"])
        qso_bearing_star = geo_bearing_star(qso_bearing)
    else:
        qso_distance = -1
        qso_bearing = -1
        qso_bearing_star = ""

    form = None
    if current_user.is_authenticated:
        form = PictureForm()
        if form.validate_on_submit():
            filename = pictures.save(form.picture.data)
            a = Picture()
            a.name = form.name.data
            a.filename = filename
            a.log_id = qso.id
            db.session.add(a)
            db.session.commit()
            return redirect(
                url_for("bp_qsos.view", username=qso.user.name, logbook_slug=qso.logbook.slug, qso_slug=qso.slug)
            )

    return render_template(
        "qsos/view.jinja2",
        qso=qso,
        qso_distance=qso_distance,
        qso_bearing=qso_bearing,
        qso_bearing_star=qso_bearing_star,
        qso_distance_unit="Km",
        new_pic=form,
        pcfg=pcfg,
        logbook=_logbook,
    )


@bp_qsos.route(
    "/logbook/<string:username>/<string:logbook_slug>/qso/<string:qso_slug>/pictures/<int:picture_id>/delete",
    methods=["GET", "POST"],
)
@check_default_profile
@login_required
def delete_picture(username, logbook_slug, qso_slug, picture_id):
    user = User.query.filter(User.name == username).first()
    if not user:
        flash("User not found")
        return redirect(url_for("bp_main.home"))

    _logbook = Logbook.query.filter(Logbook.slug == logbook_slug).first()
    if not _logbook:
        flash("Logbook not found", "error")
        return redirect(url_for("bp_logbooks.logbooks", user=user.name))

    qso = Log.query.filter(Log.slug == qso_slug, Log.logbook_id == _logbook.id).first()
    if not qso:
        flash("Qso not found", "error")
        return redirect(url_for("bp_qsos.logbook", username=user.name, logbook_slug=_logbook.slug))

    picture = Picture.query.filter(Picture.id == picture_id, Picture.log_id == qso.id).first()
    if not picture:
        flash("Picture not found", "error")
        return redirect(url_for("bp_qsos.logbook", username=user.name, logbook_slug=_logbook.slug))

    db.session.delete(picture)
    db.session.commit()

    f = os.path.join(current_app.config["UPLOADED_PICTURES_DEST"], picture.filename)
    if os.path.isfile(f):
        os.remove(f)

    return redirect(url_for("bp_qsos.view", username=user.name, logbook_slug=_logbook.slug, qso_slug=qso.slug))


@bp_qsos.route("/logbook/qso/<int:qso_id>/modal", methods=["GET"])
def single_qso_modal(qso_id):
    qso = Log.query.filter(Log.id == qso_id).first()
    if not qso.logbook.public and not current_user.is_authenticated:
        raise InvalidUsage("Qso not found", status_code=404)
    if not qso.logbook.public and qso.user_id != current_user.id:
        raise InvalidUsage("Qso not found", status_code=404)

    if not qso.gridsquare:
        qso_gs = qso.country_grid()
    else:
        qso_gs = qso.gridsquare

    if not is_valid_qth(qso.user.locator, 6):
        raise InvalidUsage("User supplied QTH is not valid", status_code=400)

    if qso_gs and not is_valid_qth(qso_gs, 6):
        raise InvalidUsage("QSO supplied QTH is not valid", status_code=400)

    if qso.user.locator and qso_gs:
        _f = qth_to_coords(qso.user.locator, 6)  # precision, latitude, longitude
        _t = qth_to_coords(qso_gs, 6)  # precision, latitude, longitude

        qso_distance = distance.haversine_km(_f["latitude"], _f["longitude"], _t["latitude"], _t["longitude"])

        qso_bearing = bearing.initial_compass_bearing(_f["latitude"], _f["longitude"], _t["latitude"], _t["longitude"])
        qso_bearing_star = geo_bearing_star(qso_bearing)
    else:
        qso_distance = -1
        qso_bearing = -1
        qso_bearing_star = ""

    return render_template(
        "qsos/_single_qso_modal.jinja2",
        qso=qso,
        qso_distance=qso_distance,
        qso_bearing=qso_bearing,
        qso_bearing_star=qso_bearing_star,
        qso_distance_unit="Km",
    )


@bp_qsos.route("/user/<string:username>/logbook/<string:logbook_slug>/stats", methods=["GET"])
@check_default_profile
def logbook_stats(username, logbook_slug):
    user = User.query.filter(User.name == username).first()
    if not user:
        flash("User not found", "error")
        return redirect(url_for("bp_main.home"))

    _logbook = Logbook.query.filter(Logbook.user_id == user.id, Logbook.slug == logbook_slug).first()
    if not _logbook:
        flash("Logbook not found", "error")
        return redirect(url_for("bp_logbooks.logbooks", user=user.name))

    if not _logbook.public and not current_user.is_authenticated:
        flash("Logbook not found", "error")
        return redirect(url_for("bp_logbooks.logbooks", user=user.name))

    if not _logbook.public and _logbook.user_id != current_user.id:
        flash("Logbook not found", "error")
        return redirect(url_for("bp_logbooks.logbooks", user=user.name))

    if current_user.is_authenticated:
        logbooks = (
            db.session.query(Logbook.id, Logbook.slug, Logbook.name, func.count(Log.id))
            .join(Log)
            .filter(Logbook.user_id == current_user.id)
            .group_by(Logbook.id)
            .all()
        )
    else:
        logbooks = (
            db.session.query(Logbook.id, Logbook.slug, Logbook.name, func.count(Log.id))
            .join(Log)
            .filter(Logbook.user_id == user.id, Logbook.public.is_(True))
            .group_by(Logbook.id)
            .all()
        )

    pcfg = {"title": "Stats for {0}".format(_logbook.name)}

    # Bargraph by year (previous and current)
    stats_months = []
    total_qsos = 0
    dt = datetime.datetime.utcnow()

    for y in [dt.year, dt.year - 1]:
        stats_y = []
        for i in range(1, 13):
            mr = monthrange(y, i)
            d_month_start = datetime.datetime(y, i, 0o1, 00, 00, 00, tzinfo=pytz.timezone("UTC"))
            d_month_end = datetime.datetime(y, i, mr[1], 23, 59, 59, tzinfo=pytz.timezone("UTC"))
            month_count = (
                db.session.query(Log.id)
                .filter(
                    Log.user_id == user.id,
                    Log.time_on.between(d_month_start, d_month_end),
                    Log.logbook_id == _logbook.id,
                )
                .count()
            )
            stats_y.append([i, month_count])
            total_qsos += month_count
        stats_months.append(stats_y)

    # Pie with modes
    stats_modes = []
    _a_logs = Bundle("log", Log.mode_id, func.count(Log.id))
    _b_modes = Bundle("modes", Mode.id, Mode.submode)
    for _modes, _logs in (
        db.session.query(_b_modes, _a_logs)
        .join(Mode.logs)
        .filter(Log.user_id == user.id, Log.logbook_id == _logbook.id)
        .group_by(Log.mode_id, Mode.id, Mode.submode)
        .all()
    ):
        stats_modes.append({"label": _modes[1], "data": _logs[1]})

    # Pie with bands
    stats_bands = []
    _a_logs = Bundle("log", Log.band_id, func.count(Log.id))
    _b_bands = Bundle("bands", Band.id, Band.name)
    for _bands, _logs in (
        db.session.query(_b_bands, _a_logs)
        .join(Band.logs)
        .filter(Log.user_id == user.id, Log.logbook_id == _logbook.id)
        .group_by(Log.band_id, Band.id, Band.name)
        .all()
    ):
        stats_bands.append({"label": _bands[1], "data": _logs[1]})

    # DXCC Awards worked
    dxcc_worked = {}
    d_b_w = (
        db.session.query(Log.country, Band.name, func.count(Log.id))
        .join(Band)
        .group_by(Band.name, Log.country)
        .filter(Log.user_id == user.id, Log.logbook_id == _logbook.id)
        .order_by(Log.country.asc())
        .all()
    )
    # Format: [(country, band_name, count), ...]
    for c in d_b_w:
        if c[0] not in dxcc_worked:
            dxcc_worked[c[0]] = {}
        dxcc_worked[c[0]][c[1]] = c[2]

    dxcc_bands = [
        bandname[0]
        for bandname in db.session.query(Band.name)
        .filter(Band.modes.is_(None), Band.start.is_(None), Band.zone == user.zone)
        .order_by(Band.lower.asc())
        .all()
    ]

    stats = {
        "current_year": stats_months[0],
        "previous_year": stats_months[1],
        "l_cy": dt.year,
        "l_py": dt.year - 1,
        "modes_used": stats_modes,
        "bands_used": stats_bands,
        "total_qsos_year": total_qsos,
        "bands_list": dxcc_bands,
        "dxcc_worked": dxcc_worked,
    }

    return render_template(
        "qsos/stats.jinja2",
        pcfg=pcfg,
        stats_json=json.dumps(stats),
        stats=stats,
        user=user,
        logbooks=logbooks,
        logbook=_logbook,
    )


@bp_qsos.route("/logbook/<string:logbook_slug>/qsos/last16", methods=["GET"])
@login_required
def last_16_qsos(logbook_slug):
    call = request.args.get("callsign", None)

    _logbook = Logbook.query.filter(Logbook.slug == logbook_slug, Logbook.user_id == current_user.id).first()

    if not _logbook or _logbook.user_id != current_user.id:
        return None

    if not call:
        qsos = (
            db.session.query(Log.time_on, Log.call, Mode.submode, Log.rst_sent, Log.rst_rcvd, Band.name)
            .join(Mode, Band)
            .filter(Log.user_id == current_user.id, Log.logbook_id == _logbook.id)
            .order_by(Log.time_on.desc())
            .limit(16)
            .all()
        )
    else:
        call = call.upper()
        qsos = (
            db.session.query(Log.time_on, Log.call, Mode.submode, Log.rst_sent, Log.rst_rcvd, Band.name)
            .join(Mode, Band)
            .filter(Log.user_id == current_user.id, Log.logbook_id == _logbook.id, Log.call.contains(call))
            .order_by(Log.time_on.desc())
            .limit(16)
            .all()
        )

    return render_template("qsos/_logbook_table.jinja2", qsos=qsos, call=call)


@bp_qsos.route("/user/<string:username>/logbook/<string:logbook_slug>/search/simple", methods=["GET"])
def logbook_search(username, logbook_slug):
    user = User.query.filter(User.name == username).first()
    if not user:
        flash("User not found", "error")
        return redirect(url_for("bp_main.home"))

    _logbook = Logbook.query.filter(Logbook.user_id == user.id, Logbook.slug == logbook_slug).first()
    if not _logbook:
        flash("Logbook not found", "error")
        return redirect(url_for("bp_logbooks.logbooks", user=user.name))

    search_term = request.args.get("q", None)
    if not search_term or search_term == "":
        flash("No search term entered", "warning")
        return redirect(url_for("bp_qsos.logbook", username=user.name, logbook_slug=_logbook.slug))

    try:
        page = int(request.args.get("page", 1))
    except ValueError:
        page = 1

    pcfg = {"title": "Search {0} from {0}'s ({1}) logbook".format(search_term, user.name, user.callsign)}

    if not _logbook.public and not current_user.is_authenticated:
        flash("Logbook not found", "error")
        return redirect(url_for("bp_logbooks.logbooks", user=user.name))

    if not _logbook.public and _logbook.user_id != current_user.id:
        flash("Logbook not found", "error")
        return redirect(url_for("bp_logbooks.logbooks", user=user.name))

    bq = (
        Log.query.filter(User.id == user.id, Log.logbook_id == _logbook.id)
        .search(search_term)
        .paginate(page=page, per_page=20)
    )

    if current_user.is_authenticated:
        logbooks = (
            db.session.query(Logbook.id, Logbook.slug, Logbook.name, func.count(Log.id))
            .join(Log)
            .filter(Logbook.user_id == current_user.id)
            .group_by(Logbook.id)
            .all()
        )
    else:
        logbooks = (
            db.session.query(Logbook.id, Logbook.slug, Logbook.name, func.count(Log.id))
            .join(Log)
            .filter(Logbook.user_id == user.id, Logbook.public.is_(True))
            .group_by(Logbook.id)
            .all()
        )

    return render_template(
        "qsos/search.jinja2",
        logbooks=logbooks,
        qsos=bq,
        logbook=_logbook,
        user=user,
        search_term=search_term,
        pcfg=pcfg,
    )


@bp_qsos.route("/user/<string:username>/logbook/<string:logbook_slug>/search/advanced", methods=["GET", "POST"])
def logbook_search_adv(username, logbook_slug):
    user = User.query.filter(User.name == username).first()
    if not user:
        flash("User not found", "error")
        return redirect(url_for("bp_main.home"))

    _logbook = Logbook.query.filter(Logbook.user_id == user.id, Logbook.slug == logbook_slug).first()
    if not _logbook:
        flash("Logbook not found", "error")
        return redirect(url_for("bp_logbooks.logbooks", user=user.name))

    pcfg = {"title": "Adv Search from {0}'s ({1}) logbook".format(user.name, user.callsign)}

    if not _logbook.public and not current_user.is_authenticated:
        flash("Logbook not found", "error")
        return redirect(url_for("bp_logbooks.logbooks", user=user.name))

    if not _logbook.public and _logbook.user_id != current_user.id:
        flash("Logbook not found", "error")
        return redirect(url_for("bp_logbooks.logbooks", user=user.name))

    if current_user.is_authenticated:
        logbooks = (
            db.session.query(Logbook.id, Logbook.slug, Logbook.name, func.count(Log.id))
            .join(Log)
            .filter(Logbook.user_id == current_user.id)
            .group_by(Logbook.id)
            .all()
        )
    else:
        logbooks = (
            db.session.query(Logbook.id, Logbook.slug, Logbook.name, func.count(Log.id))
            .join(Log)
            .filter(Logbook.user_id == user.id, Logbook.public.is_(True))
            .group_by(Logbook.id)
            .all()
        )

    if request.method == "GET":
        form = AdvSearchForm()
    else:
        form = AdvSearchForm(request.form)

    filter_modes = []
    _a_logs = Bundle("log", Log.mode_id)
    _b_modes = Bundle("modes", Mode.id, Mode.mode, Mode.submode)
    for _modes, _logs in (
        db.session.query(_b_modes, _a_logs)
        .join(Mode.logs)
        .filter(Log.user_id == user.id, Log.logbook_id == _logbook.id)
        .group_by(_a_logs, _b_modes)
        .all()
    ):
        filter_modes.append([_modes.id, "{0} - {1}".format(_modes.mode, _modes.submode)])

    filter_bands = []
    _a_logs = Bundle("log", Log.band_id)
    _b_bands = Bundle("bands", Band.id, Band.name)
    for _bands, _logs in (
        db.session.query(_b_bands, _a_logs)
        .join(Band.logs)
        .filter(Log.user_id == user.id, Log.logbook_id == _logbook.id)
        .group_by(_a_logs, _b_bands)
        .all()
    ):
        filter_bands.append([_bands.name, _bands.name])

    filter_countries = []
    for _log in db.session.query(Log.country).group_by(Log.country).order_by(Log.country).all():
        filter_countries.append([_log.country, _log.country])

    filter_modes.insert(0, ["any", "Any mode"])
    filter_bands.insert(0, ["any", "Any band"])
    filter_countries.insert(0, ["any", "Any country"])

    if request.method == "GET":
        form.country.data = "any"
        form.mode.data = "any"
        form.band.data = "any"

    form.country.choices = filter_countries
    form.mode.choices = filter_modes
    form.band.choices = filter_bands

    bq = Log.query.filter(User.id == user.id, Log.logbook_id == _logbook.id)
    filtered = False

    if form.country.data != "any":
        filtered = True
        bq = bq.filter(Log.country == form.country.data)

    if form.mode.data != "any":
        filtered = True
        bq = bq.filter(Log.mode_id == form.mode.data)

    if form.band.data != "any":
        band_id = Band.query.filter(Band.name == form.band.data).first()
        if not band_id:
            flash("Invalid band", "warning")
        else:
            filtered = True
            bq = bq.filter(Log.band_id == band_id.id)

    if form.frequency.data != "" and form.frequency.data is not None:
        filtered = True
        bq = bq.filter(Log.freq == form.frequency.data)

    if form.call.data != "" and form.call.data is not None:
        filtered = True
        bq = bq.filter(Log.call.ilike(form.call.data))

    if form.fts.data != "" and form.fts.data is not None:
        filtered = True
        bq = bq.search(form.fts.data)

    if form.pictures.data == "Y":
        filtered = True
        bq = bq.filter(Log.pictures)
    elif form.pictures.data == "N":
        bq = bq.filter(Log.pictures == None)  # noqa: E711, the " == " seems mandatory for sqlalchemy

    if not filtered:
        bq = bq.limit(20)

    qsos = bq.all()

    return render_template(
        "qsos/adv_search.jinja2",
        qsos=qsos,
        form=form,
        logbooks=logbooks,
        logbook=_logbook,
        user=user,
        filtered=filtered,
        pcfg=pcfg,
    )


@bp_qsos.route("/user/<string:username>/logbook/<string:logbook_slug>/map", methods=["GET"])
@check_default_profile
def map(username, logbook_slug):
    user = User.query.filter(User.name == username).first()
    if not user:
        flash("User not found", "error")
        return redirect(url_for("bp_main.home"))

    pcfg = {"title": "{0}'s ({1}) logbook map".format(user.name, user.callsign)}

    _logbook = Logbook.query.filter(Logbook.slug == logbook_slug, Logbook.user_id == user.id).first()
    if not _logbook:
        flash("Logbook not found", "error")
        return redirect(url_for("bp_logbooks.logbooks", user=user.name))

    if not _logbook.public and not current_user.is_authenticated:
        flash("Logbook not found", "error")
        return redirect(url_for("bp_logbooks.logbooks", user=user.name))

    if not _logbook.public and _logbook.user_id != current_user.id:
        flash("Logbook not found", "error")
        return redirect(url_for("bp_logbooks.logbooks", user=user.name))

    if is_valid_qth(user.locator, 6):
        uqth = user.qth_to_coords()
    else:
        flash("User gridsquare is invalid")
        return redirect(url_for("bp_logbooks.logbooks", user=user.name))

    if current_user.is_authenticated:
        logbooks = (
            db.session.query(Logbook.id, Logbook.slug, Logbook.name, func.count(Log.id))
            .join(Log)
            .filter(Logbook.user_id == current_user.id)
            .group_by(Logbook.id)
            .all()
        )
    else:
        logbooks = (
            db.session.query(Logbook.id, Logbook.slug, Logbook.name, func.count(Log.id))
            .join(Log)
            .filter(Logbook.user_id == user.id, Logbook.public.is_(True))
            .group_by(Logbook.id)
            .all()
        )

    return render_template("qsos/map.jinja2", pcfg=pcfg, user=user, logbook=_logbook, uqth=uqth, logbooks=logbooks)
