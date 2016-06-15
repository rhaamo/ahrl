# coding: utf8
from flask import Blueprint, render_template, redirect, url_for, stream_with_context, Response, flash
from flask_security import login_required, current_user
from models import db, Log, Mode, Band, User, Logbook, Band
from utils import check_default_profile, ADIF_FIELDS, InvalidUsage
from adif import parse as adif_parser
from forms import AdifParse
from werkzeug.utils import secure_filename
import datetime
import pytz

bp_tools = Blueprint('bp_tools', __name__)


@bp_tools.route('/tools/adif/import', methods=['GET'])
@login_required
@check_default_profile
def adif_import():
    pcfg = {"title": "Import ADIF"}
    form = AdifParse()
    return render_template('tools/adif_import.jinja2', pcfg=pcfg, form=form)


@bp_tools.route('/logbooks/adif/import', methods=['POST'])
@login_required
@check_default_profile
def adif_import_file():
    pcfg = {"title": "Import ADIF"}
    form = AdifParse()
    if form.validate_on_submit():
        filename = secure_filename(form.adif_file.data.filename)
        files = form.adif_file.raw_data[0].stream.read()
        form.adif_file.raw_data[0].close()

        parsed_adif = adif_parser(files)
        count = 0
        duplicates = 0

        for log in parsed_adif:
            # First check if duplicate
            _date = "{0} {1}".format(log['qso_date'], log['time_on'])
            _date_wo_tz = datetime.datetime.strptime(_date, "%Y%m%d %H%M%S")
            duplicates_count = db.session.query(Log.id).filter(Log.user_id == current_user.id,
                                                               Log.call == log['call'],
                                                               Log.time_on == _date_wo_tz,
                                                               Log.logbook_id == form.logbook.raw_data[0]).count()
            if duplicates_count > 0:
                duplicates += 1
                continue  # duplicate found, skip record

            l = Log()
            for key in ADIF_FIELDS:
                if key not in log:
                    continue

                setattr(l, key, log[key])
            # other fields to manage specifically
            if 'class' in log:
                l.klass = log['class']
            if 'band' in log:
                band = Band.query.filter(Band.name == log['band'],
                                         Band.start.is_(None),
                                         Band.modes.is_(None)).first()
                if not band:
                    band = Band.query.filter(Band.name == 'SSB',
                                             Band.start.is_(None),
                                             Band.modes.is_(None)).first()
                    if not l.notes:
                        l.notes = ""
                    l.notes += "\r\nBand automatically set to 40m because not found in ADIF"
                l.band_id = band.id
            if 'freq' in log:
                l.freq = int(float(log['freq']) * 1000000)  # ADIF stores in MHz, we store in Hertz
            if 'freq_rx' in log:
                l.freq_rx = int(float(log['freq_rx']) * 1000000)  # Same as freq
            if 'mode' in log:
                mode = Mode.query.filter(Mode.mode == log['mode']).first()
                if not mode:
                    mode = Mode.query.filter(Mode.mode == 'SSB').first()
                    if not l.notes:
                        l.notes = ""
                    l.notes += "\r\nMode automatically set to SSB because not found in ADIF"
                l.mode_id = mode.id
            # Reminder : ADIF is in UTC, we store in UTC, no TZ conversion necessary
            if 'qso_date' in log and 'time_on':
                date = "{0} {1}".format(log['qso_date'], log['time_on'])
                date_wo_tz = datetime.datetime.strptime(date, "%Y%m%d %H%M%S")
                l.time_on = date_wo_tz
                l.time_off = date_wo_tz
            else:
                date_w_tz = datetime.datetime.utcnow()
                l.time_on = date_w_tz.astimezone(pytz.timezone('UTC'))
                l.time_off = date_w_tz.astimezone(pytz.timezone('UTC'))
                if not l.notes:
                    l.notes = ""
                l.notes = "\r\nDate set to the import date because not found in ADIF"
            if 'comment' in log:
                l.comment = log['comment']
            if 'comment_intl' in log:
                l.comment = log['comment_intl']
            l.user = current_user  # oops dont miss it
            l.logbook_id = form.logbook.raw_data[0]

            db.session.add(l)
            count += 1  # One more in the stack
        db.session.commit()

        flash('Imported {0} ({1} duplicates) QSOs from {2}'.format(count, duplicates, filename), 'info')
    else:
        return render_template('tools/adif_import.jinja2', pcfg=pcfg, form=form, flash='Error with the file')

    return redirect(url_for('bp_qsos.logbook', username=current_user.name, logbook_id=form.logbook.raw_data[0]))


@bp_tools.route('/logbook/<string:username>/<int:logbook_id>/adif/export', methods=['GET'])
@login_required
def adif_export_dl(username, logbook_id):
    user = User.query.filter(User.name == username).first()
    if not user:
        raise InvalidUsage("User not found", 404)
    logbook = Logbook.query.filter(Logbook.user_id == user.id, Logbook.id == logbook_id).first()
    if not logbook or (current_user.id != user.id):
        raise InvalidUsage("Logbook not found", 404)

    logs = logbook.logs

    def a(k, v):
        v = str(v)
        return u"<{0}:{1}>{2} ".format(k, len(v), v)

    def generate():
        yield 'ADIF Export by AHRL\r\n'
        yield '\r\n'
        yield '<adif_ver:5>3.0.4\r\n'
        yield '<programid:4>AHRL\r\n'
        yield a('station_callsign', user.callsign) + '\r\n'
        yield a('operator', user.callsign) + '\r\n'
        yield '\r\n'
        yield '<eoh>\r\n\r\n'

        for log in logs:
            counter = 0
            for key in ADIF_FIELDS:
                if counter == 4:
                    counter = 0
                    yield '\r\n'

                value = getattr(log, key)
                if value:
                    yield a(key, value)
                    counter += 1

            yield '\r\n'
            # Manual ones
            if log.freq:
                yield a('freq', log.freq / 1000000.0)
            if log.freq_rx:
                yield a('freq', log.freq_rx / 1000000.0)
            if log.mode:
                yield a('mode', log.mode.mode)
            if log.time_on:
                yield a('qso_date', log.time_on.strftime('%Y%m%d'))
                yield a('time_on', log.time_on.strftime('%H%M%S'))
            if log.klass:
                yield a('class', log.klass)
            if log.band:
                yield a('band', log.band.name)
            if log.comment:
                yield a('comment_intl', log.comment)
            yield '\r\n<eor>\r\n\r\n'

    return Response(stream_with_context(generate()), mimetype="text/plain",
                    headers={"Content-Disposition": "attachment;filename=qsos-{0}.adi".format(user.name)})


@bp_tools.route('/tools/bands/plan', methods=['GET'])
@check_default_profile
def bands_plan():
    pcfg = {"title": "IARU Band Plans"}
    bands = {
        'iaru1': {
            'name': 'IARU Zone 1',
            'slug': 'iaru1',
            'bands': Band.query.filter(Band.modes.is_(None), Band.start.is_(None), Band.zone == 'iaru1').all()
        },
        'iaru2': {
            'name': 'IARU Zone 2',
            'slug': 'iaru2',
            'bands': Band.query.filter(Band.modes.is_(None), Band.start.is_(None), Band.zone == 'iaru2').all()
        },
        'iaru3': {
            'name': 'IARU Zone 3',
            'slug': 'iaru3',
            'bands': Band.query.filter(Band.modes.is_(None), Band.start.is_(None), Band.zone == 'iaru3').all()
        }
    }
    return render_template('tools/bands_plan.jinja2', pcfg=pcfg, bands=bands)
