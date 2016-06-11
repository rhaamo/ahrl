from flask import Blueprint, render_template, request, redirect, url_for
from flask_security import login_required, current_user
from models import db, User, Logbook
from forms import UserProfileForm
from utils import check_default_profile

bp_users = Blueprint('bp_users', __name__)


@bp_users.route('/user', methods=['GET'])
@login_required
@check_default_profile
def profile():
    pcfg = {"title": "My Profile"}
    user = User.query.get_or_404(current_user.id)
    logbooks = Logbook.query.filter(Logbook.user_id == current_user.id).all()
    return render_template('users/profile.jinja2', pcfg=pcfg, user=user, logbooks=logbooks)


@bp_users.route('/user/edit', methods=['GET', 'POST'])
@login_required
def edit():
    pcfg = {"title": "Edit my profile"}
    a = User.query.get_or_404(current_user.id)

    form = UserProfileForm(request.form, a)

    if form.validate_on_submit():
        a.callsign = form.callsign.data
        a.lastname = form.lastname.data
        a.firstname = form.firstname.data
        a.timezone = form.timezone.data
        a.locator = form.locator.data
        a.lotw_name = form.lotw_name.data
        a.lotw_password = form.lotw_password.data
        a.eqsl_name = form.eqsl_name.data
        a.eqsl_password = form.eqsl_password.data
        a.swl = form.swl.data

        db.session.commit()
        return redirect(url_for('bp_users.profile'))

    logbooks = Logbook.query.filter(Logbook.user_id == current_user.id).all()
    return render_template('users/edit.jinja2', pcfg=pcfg, form=form, user=a, logbooks=logbooks)
