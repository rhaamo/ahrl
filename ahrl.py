# encoding: utf-8
from pprint import pprint as pp

from flask import Flask, render_template, g, send_from_directory, jsonify
from flask_security import Security, current_user
from flask_script import Manager
from flask_migrate import Migrate, MigrateCommand
from flask_mail import Mail
from flask_bootstrap import Bootstrap
from flask_debugtoolbar import DebugToolbarExtension

from models import db, user_datastore

from controllers.main import bp_main
from controllers.users import bp_users
from controllers.notes import bp_notes
from controllers.qsos import bp_qsos
from controllers.tools import bp_tools
from controllers.contacts import bp_contacts
from crons import update_qsos_without_countries

import texttable
from dbseed import make_db_seed
from forms import ExtendedRegisterForm

import os
import subprocess

from utils import dt_utc_to_user_tz, InvalidUsage, show_date_no_offset

import logging
from logging.handlers import RotatingFileHandler

__VERSION__ = "0.0.1"

# App Configuration
app = Flask(__name__)
Bootstrap(app)

app.jinja_env.add_extension('jinja2.ext.with_')
app.jinja_env.add_extension('jinja2.ext.do')
app.jinja_env.filters['localize'] = dt_utc_to_user_tz
app.jinja_env.filters['show_date_no_offset'] = show_date_no_offset

app.config.from_pyfile("config.py")

# Logging
if not app.debug:
    formatter = logging.Formatter('%(asctime)s %(levelname)s: %(message)s [in %(pathname)s:%(lineno)d]')
    file_handler = RotatingFileHandler("%s/errors_app.log" % os.getcwd(), 'a', 1000000, 1)
    file_handler.setLevel(logging.DEBUG)
    file_handler.setFormatter(formatter)
    app.logger.addHandler(file_handler)

toolbar = DebugToolbarExtension(app)
mail = Mail(app)

db.init_app(app)

migrate = Migrate(app, db)

manager = Manager(app)

# Setup Flask-Security
security = Security(app, user_datastore,
                    register_form=ExtendedRegisterForm)

git_version = ""
gitpath = os.path.join(os.getcwd(), ".git")
if os.path.isdir(gitpath):
    git_version = subprocess.check_output(['git', 'rev-parse', '--short', 'HEAD'])
    if git_version:
        git_version = git_version.strip()


@app.before_request
def before_request():
    g.cfg = {
        'AHRL_VERSION': "{0} ({1})".format(__VERSION__, git_version),
    }
    g.current_user = current_user


@app.errorhandler(InvalidUsage)
def handle_invalid_usage(error):
    response = jsonify(error.to_dict())
    response.status_code = error.status_code
    return response

app.register_blueprint(bp_main)
app.register_blueprint(bp_users)
app.register_blueprint(bp_notes)
app.register_blueprint(bp_qsos)
app.register_blueprint(bp_tools)
app.register_blueprint(bp_contacts)


# Used in development
@app.route('/uploads/<path:stuff>', methods=['GET'])
def get_uploads_stuff(stuff):
    print("Get {0} from {1}".format(stuff, app.config['UPLOADS_DEFAULT_DEST']))
    return send_from_directory(['UPLOADS_DEFAULT_DEST'], stuff, as_attachment=False)


@app.errorhandler(404)
def page_not_found(e):
    pcfg = {"title": "Whoops, something failed.",
            "error": 404, "message": "Page not found", "e": e}
    return render_template('error_page.jinja2', pcfg=pcfg), 404


@app.errorhandler(403)
def err_forbidden(e):
    pcfg = {"title": "Whoops, something failed.",
            "error": 403, "message": "Access forbidden", "e": e}
    return render_template('error_page.jinja2', pcfg=pcfg), 403


@app.errorhandler(410)
def err_gone(e):
    pcfg = {"title": "Whoops, something failed.",
            "error": 410, "message": "Gone", "e": e}
    return render_template('error_page.jinja2', pcfg=pcfg), 410


if not app.debug:
    @app.errorhandler(500)
    def err_failed(e):
        pcfg = {"title": "Whoops, something failed.", "error": 500, "message": "Something is broken", "e": e}
        return render_template('error_page.jinja2', pcfg=pcfg), 500


# Other commands
@manager.command
def dump_routes():
    """Dump all routes of defined app"""
    table = texttable.Texttable()
    table.set_deco(texttable.Texttable().HEADER)
    table.set_cols_dtype(['t', 't', 't'])
    table.set_cols_align(["l", "l", "l"])
    table.set_cols_width([60, 30, 90])

    table.add_rows([["Prefix", "Verb", "URI Pattern"]])

    for rule in sorted(app.url_map.iter_rules(), key=lambda x: x.match_compare_key()):
        methods = ','.join(rule.methods)
        table.add_row([rule.endpoint, methods, rule])

    print(table.draw())


@manager.command
def config():
    """Dump config"""
    pp(app.config)


@manager.command
def db_seed():
    """Seed database with default content"""
    make_db_seed(db)


@manager.command
def cron_update_qsos_countries():
    """Update QSOs with empty country"""
    update_qsos_without_countries(db)


manager.add_command('db', MigrateCommand)

if __name__ == '__main__':
    manager.run()
