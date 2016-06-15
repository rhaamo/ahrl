from flask import Blueprint, render_template, request, redirect, url_for, flash
from flask_security import login_required, current_user
from models import db, User, Logbook
from forms import UserProfileForm
from utils import check_default_profile
import pytz

bp_users = Blueprint('bp_users', __name__)


@bp_users.route('/user', methods=['GET'])
@login_required
@check_default_profile
def profile():
    pcfg = {"title": "My Profile"}

    user = User.query.filter(User.id == current_user.id).first()
    if not user:
        flash("User not found", 'error')
        return redirect(url_for("bp_main.home"))

    logbooks = Logbook.query.filter(Logbook.user_id == current_user.id).all()
    return render_template('users/profile.jinja2', pcfg=pcfg, user=user, logbooks=logbooks)


@bp_users.route('/user/edit', methods=['GET', 'POST'])
@login_required
def edit():
    pcfg = {"title": "Edit my profile"}

    user = User.query.filter(User.id == current_user.id).first()
    if not user:
        flash("User not found", 'error')
        return redirect(url_for("bp_main.home"))

    form = UserProfileForm(request.form, user)
    form.timezone.choices = [[str(i), str(i)] for i in pytz.all_timezones]

    if form.validate_on_submit():
        user.callsign = form.callsign.data
        user.lastname = form.lastname.data
        user.firstname = form.firstname.data
        user.timezone = form.timezone.data
        user.locator = form.locator.data
        user.lotw_name = form.lotw_name.data
        user.lotw_password = form.lotw_password.data
        user.eqsl_name = form.eqsl_name.data
        user.eqsl_password = form.eqsl_password.data
        user.swl = form.swl.data
        user.zone = form.zone.data

        db.session.commit()
        return redirect(url_for('bp_users.profile'))

    logbooks = Logbook.query.filter(Logbook.user_id == current_user.id).all()
    return render_template('users/edit.jinja2', pcfg=pcfg, form=form, user=user, logbooks=logbooks)
