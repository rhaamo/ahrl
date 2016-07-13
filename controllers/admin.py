from flask import Blueprint, render_template, request, redirect, url_for, flash
from flask_security import login_required

from forms import ConfigForm
from models import db, Logging, Config
from utils import check_default_profile, is_admin

bp_admin = Blueprint('bp_admin', __name__)


@bp_admin.route('/admin/logs', methods=['GET'])
@login_required
@check_default_profile
def logs():
    if not is_admin():
        return redirect(url_for('bp_home.home'))
    pcfg = {"title": "Application Logs"}
    _logs = Logging.query.order_by(Logging.timestamp.desc()).limit(100).all()
    return render_template('admin/logs.jinja2', pcfg=pcfg, logs=_logs)


@bp_admin.route('/admin/config', methods=['GET', 'POST'])
@login_required
@check_default_profile
def config():
    if not is_admin():
        return redirect(url_for('bp_main.home'))

    pcfg = {"title": "Application Config"}

    _config = Config.query.one()
    if not _config:
        flash("Config not found", 'error')
        return redirect(url_for("bp_main.home"))

    form = ConfigForm(request.form, _config)

    if form.validate_on_submit():
        _config.clublog_api_key = form.clublog_api_key.data
        _config.eqsl_download_url = form.eqsl_download_url.data
        _config.eqsl_rcvd_mark = form.eqsl_rcvd_mark.data
        _config.eqsl_upload_url = form.eqsl_upload_url.data
        _config.lotw_download_url = form.lotw_download_url.data
        _config.lotw_upload_url = form.lotw_upload_url.data
        _config.lotw_login_url = form.lotw_login_url.data
        _config.lotw_rcvd_mark = form.lotw_rcvd_mark.data

        db.session.commit()
        flash("Configuration updated", "info")
        return redirect(url_for('bp_admin.config'))

    return render_template('admin/config.jinja2', pcfg=pcfg, form=form)
