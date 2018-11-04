from flask import Blueprint, render_template, request, redirect, url_for, flash
from flask_security import login_required, current_user
from sqlalchemy import func

from forms import LogbookForm, EditLogbookForm
from models import db, Logbook, User, Log
from utils import check_default_profile

bp_logbooks = Blueprint("bp_logbooks", __name__)


@bp_logbooks.route("/logbooks/<string:user>", methods=["GET"])
@check_default_profile
def logbooks(user):
    user = User.query.filter(User.name == user).first()
    if not user:
        flash("User not found", "error")
        return redirect(url_for("bp_main.home"))

    pcfg = {"title": "{0}'s logbooks".format(user.name)}

    if current_user.is_authenticated:
        _logbooks = (
            db.session.query(Logbook.id, Logbook.name, func.count(Log.id))
            .join(Log)
            .filter(Logbook.user_id == current_user.id)
            .group_by(Logbook.id)
            .all()
        )
    else:
        _logbooks = (
            db.session.query(Logbook.id, Logbook.name, func.count(Log.id))
            .join(Log)
            .filter(Logbook.user_id == user.id, Logbook.public.is_(True))
            .group_by(Logbook.id)
            .all()
        )

    return render_template("logbooks/logbooks.jinja2", pcfg=pcfg, user=user, logbooks=_logbooks)


@bp_logbooks.route("/logbooks/<string:logbook_slug>/edit", methods=["GET", "POST"])
@login_required
@check_default_profile
def edit(logbook_slug):
    pcfg = {"title": "Edit my logbooks"}
    a = Logbook.query.filter(Logbook.user_id == current_user.id, Logbook.slug == logbook_slug).first()
    if not a:
        flash("Logbook not found", "error")
        return redirect(url_for("bp_logbooks.logbooks", user=current_user.name))

    form = EditLogbookForm(request.form, obj=a)

    if form.validate_on_submit():
        a.name = form.name.data
        a.callsign = form.callsign.data
        a.locator = form.locator.data
        a.eqsl_qth_nickname = form.eqsl_qth_nickname.data
        a.public = form.public.data
        a.swl = form.swl.data
        a.user_id = current_user.id
        a.default = form.default.data
        a.old = form.old.data

        if a.default:
            for logbook in current_user.logbooks:
                if logbook.id == a.id:
                    continue
                logbook.default = False
        else:
            fl = current_user.logbooks.first()
            fl.default = True

        db.session.commit()
        flash("Success saving logbook: {0}".format(a.name), "success")
        return redirect(url_for("bp_logbooks.logbooks", user=current_user.name))

    return render_template("logbooks/edit.jinja2", pcfg=pcfg, form=form, logbook=a, logbook_slug=logbook_slug)


@bp_logbooks.route("/logbooks/new", methods=["GET", "POST"])
@login_required
@check_default_profile
def new():
    pcfg = {"title": "New logbook"}

    form = LogbookForm()

    if request.method == "GET":
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
        a.eqsl_qth_nickname = form.eqsl_qth_nickname.data
        a.public = form.public.data
        a.swl = form.swl.data
        a.user_id = current_user.id
        a.default = form.default.data

        if form.default.data:
            cur_dflt = Logbook.query.filter(Logbook.user_id == current_user.id, Logbook.default.is_(True)).all()
            for l in cur_dflt:
                l.default = False
        else:
            fl = Logbook.query.filter(Logbook.user_id == current_user.id).first()
            if fl:
                fl.default = True
            else:
                a.default = True

        db.session.add(a)
        db.session.commit()

        flash("Success creating logbook: {0}".format(a.name), "success")
        return redirect(url_for("bp_logbooks.logbooks", user=current_user.name))

    return render_template("logbooks/new.jinja2", pcfg=pcfg, form=form)


@bp_logbooks.route("/logbooks/<string:logbook_slug>/delete", methods=["GET", "DELETE", "PUT"])
@login_required
@check_default_profile
def delete(logbook_slug):
    logbook = Logbook.query.filter(Logbook.user_id == current_user.id, Logbook.slug == logbook_slug).first()
    if not logbook:
        flash("Logbook not found", "error")
        return redirect(url_for("bp_logbooks.logbooks", user=current_user.name))

    db.session.delete(logbook)
    db.session.commit()

    flash("Success deleting logbook: {0}".format(logbook.name), "success")

    return redirect(url_for("bp_logbooks.logbooks", user=current_user.name))
