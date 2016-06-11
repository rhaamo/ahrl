from flask import Blueprint, render_template, request, redirect, url_for, flash, Response, json
from flask_security import login_required, current_user
from models import db, Logbook, User
from forms import LogbookForm
from utils import check_default_profile, InvalidUsage, dt_utc_to_user_tz
from libqth import is_valid_qth, qth_to_coords
from geohelper import distance, bearing
from libjambon import geo_bearing_star

bp_logbooks = Blueprint('bp_logbooks', __name__)


@bp_logbooks.route('/logbooks/<string:user>', methods=['GET'])
@check_default_profile
def logbooks(user):
    user = User.query.filter(User.name == user).first()
    pcfg = {"title": "{0}'s logbooks".format(user.name)}
    return render_template('logbooks/logbooks.jinja2', pcfg=pcfg, user=user)


@bp_logbooks.route('/logbooks/<int:logbook_id>/edit', methods=['GET', 'POST'])
@login_required
@check_default_profile
def edit(logbook_id):
    pcfg = {"title": "Edit my logbooks"}
    a = Logbook.query.get_or_404(logbook_id)

    form = LogbookForm(request.form, a)

    if form.validate_on_submit():
        a.name = form.name.data
        a.callsign = form.callsign.data
        a.locator = form.locator.data
        a.public = form.public.data
        a.swl = form.swl.data
        a.user_id = current_user.id
        a.default = form.default.data

        if a.default:
            for logbook in current_user.logbooks:
                if logbook.id == a.id:
                    continue
                logbook.default = False
        else:
            fl = current_user.logbooks.first()
            fl.default = True

        db.session.commit()
        flash("Success saving logbook: {0}".format(a.name), 'success')
        return redirect(url_for('bp_logbooks.logbooks', user=current_user.name))

    return render_template('logbooks/edit.jinja2', pcfg=pcfg, form=form, logbook=a, logbook_id=logbook_id)


@bp_logbooks.route('/logbooks/new', methods=['GET', 'POST'])
@login_required
@check_default_profile
def new():
    pcfg = {"title": "New logbook"}

    form = LogbookForm()

    if request.method == 'GET':
        form.callsign.data = current_user.callsign
        form.locator.data = current_user.locator
        form.default.data = False
        form.public.data = True
        form.swl.data = current_user.swl

    if form.validate_on_submit():
        a = Logbook()
        a.name = form.name.data
        a.callsign = form.callsign.data
        a.locator = form.locator.data
        a.public = form.public.data
        a.swl = form.swl.data
        a.user_id = current_user.id
        a.default = form.default.data

        if form.default.data:
            cur_dflt = Logbook.query.filter(
                Logbook.user_id == current_user.id,
                Logbook.default.is_(True)
            ).all()
            for l in cur_dflt:
                l.default = False
        else:
            fl = Logbook.query.filter(Logbook.user_id == current_user.id).first()
            fl.default = True

        db.session.add(a)
        db.session.commit()
        flash("Success updating logbook: {0}".format(a.name), 'success')
        return redirect(url_for('bp_logbooks.logbooks', user=current_user.name))

    return render_template('logbooks/new.jinja2', pcfg=pcfg, form=form)


@bp_logbooks.route('/logbooks/<int:logbook_id>/delete', methods=['GET', 'DELETE', 'PUT'])
@login_required
@check_default_profile
def delete(logbook_id):
    logbook = Logbook.query.get_or_404(logbook_id)
    db.session.delete(logbook)
    db.session.commit()
    flash("Success deleting logbook: {0}".format(logbook.name), 'success')
    return redirect(url_for('bp_logbooks.logbooks', user=current_user.name))
