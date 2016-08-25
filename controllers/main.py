from flask import Blueprint, render_template, flash, abort
from flask_security import current_user
from sqlalchemy import func

from models import db, User, Logbook, Log, DxccEntities, DxccExceptions, DxccPrefixes

bp_main = Blueprint('bp_main', __name__)


# Show public logbooks
@bp_main.route('/')
def home():
    # Sanity check
    _dp = db.session.query(DxccPrefixes.id).count()
    _dx = db.session.query(DxccExceptions.id).count()
    _de = db.session.query(DxccEntities.id).count()
    # Count as of 25/08/16 was:
    # 3665     16435     401
    # check are lowered to avoid changing them maybe too frequently
    if _dp < 3500 or _dx < 16300 or _de < 300:
        flash("DXCC Tables are empty, check manual", "error")
        abort(500)

    pcfg = {"title": "AHRL - Another Ham Radio Log"}
    users = User.query.all()

    logbooks = None
    if current_user.is_authenticated:
        logbooks = db.session.query(Logbook.id, Logbook.slug, Logbook.name, func.count(Log.id)).join(
            Log).filter(Logbook.user_id == current_user.id).group_by(Logbook.id).all()

    return render_template('home.jinja2', pcfg=pcfg, users=users, logbooks=logbooks)


@bp_main.route('/about')
def about():
    pcfg = {"title": "About AHRL - Another Ham Radio Log"}
    return render_template('about.jinja2', pcfg=pcfg)
