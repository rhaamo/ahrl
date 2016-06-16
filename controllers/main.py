from flask import Blueprint, render_template
from models import db, User, Logbook, Log
from flask_security import current_user
from sqlalchemy import func

bp_main = Blueprint('bp_main', __name__)


# Show public logbooks
@bp_main.route('/')
def home():
    pcfg = {"title": "AHRL - Another Ham Radio Log"}
    users = User.query.all()

    logbooks = None
    if current_user.is_authenticated:
        logbooks = db.session.query(Logbook.id, Logbook.name, func.count(Log.id)).join(
            Log).filter(Logbook.user_id == current_user.id).group_by(Logbook.id).all()

    return render_template('home.jinja2', pcfg=pcfg, users=users, logbooks=logbooks)


@bp_main.route('/about')
def about():
    pcfg = {"title": "About AHRL - Another Ham Radio Log"}
    return render_template('about.jinja2', pcfg=pcfg)
