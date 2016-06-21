from flask import Blueprint, render_template, request, redirect, url_for, flash
from flask_security import login_required, current_user
from models import db, User, Logbook, Log, Logging, Config
from forms import ConfigForm
from utils import check_default_profile, is_admin
import pytz
from sqlalchemy import func


bp_admin = Blueprint('bp_admin', __name__)


@bp_admin.route('/admin/logs', methods=['GET'])
@login_required
@check_default_profile
def logs():
    if not is_admin():
        return redirect(url_for('bp_home.home'))
    pcfg = {"title": "Application Logs"}
    logs = Logging.query.order_by(Logging.timestamp).limit(100).all()
    return render_template('users/user_logs.jinja2', pcfg=pcfg, logs=logs)


@bp_admin.route('/admin/config', methods=['GET', 'POST'])
@login_required
@check_default_profile
def config():
    if not is_admin():
        return redirect(url_for('bp_main.home'))

    pcfg = {"title": "Application Config"}

    config = Config.query.one()
    if not config:
        flash("Config not found", 'error')
        return redirect(url_for("bp_main.home"))

    form = ConfigForm(request.form, config)

    if form.validate_on_submit():
        config.clublog_api_key = form.clublog_api_key.data
        config.eqsl_download_url = form.eqsl_download_url.data
        config.eqsl_rcvd_mark = form.eqsl_rcvd_mark.data
        config.eqsl_upload_url = form.eqsl_upload_url.data
        config.lotw_download_url = form.lotw_download_url.data
        config.lotw_upload_url = form.lotw_upload_url.data
        config.lotw_login_url = form.lotw_login_url.data
        config.lotw_rcvd_mark = form.lotw_rcvd_mark.data

        db.session.commit()
        return redirect(url_for('bp_admin.config'))

    return render_template('admin/config.jinja2', pcfg=pcfg, form=form)
