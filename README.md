Another Ham Radio Log
=====================

# Versions requirement
 - Python 3

# Installation
    Install a BDD (sqlite, mysql, postgresql)
    Makes sure that encoding is/will be in UNICODE/UTF-8
    git clone http://dev.sigpipe.me/DashieHam/ahrl
    cd ahrl
    git submodule init
    git submodule update
    pip install --requirement requirements.txt  # if present
    cp config.py.sample config.py
    $EDITOR config.py
    python ahrl.py db upgrade
    python ahrl.py db_seed
    python ahrl.py runserver # or whatever gunicorn whatever stuff

# Gunicorn
    gunicorn -w 2 -b 127.0.0.1:8000 --error-logfile=errors.log --access-logfile=access.log --chdir=$PWD ahrl:app

# Crontabs
  List of cron target availables.
  Makes sure to run them under the user which runs ahrl and virtualenv if you use it.
  Commands:
  - python ahrl.py cron_update_qsos_countries  # Update all QSOs if missing a Country/DXCC entry by using ClubLog

# Licensing
 - MIT License

# Fork from
 - This is majoritary a fork of https://github.com/magicbug/Cloudlog by 2E0SQL
 - Thanks to him for all his work on CloudLog which inspired me (and from which I reused some things)

# How we handle DateTimes and timezones
 - DateTimes are stored in database without timezone, so we manage to always save them in UTC:


    time_off = db.Column(db.DateTime(timezone=False), default=None)
    time_on = db.Column(db.DateTime(timezone=False), default=None, index=True)

 - User input DateTime are first converted to a timezone-aware DateTime of 'current_user.timezone' (using pytz)
 - Then are converted .astimezone() to UTC, still with pytz and stored in database

 - The reverse, DB -> View are either:
   - Using a function (utils: dt_utc_to_user_tz(dt, user=None)) or jinja2 helper (localize, mapped to dt_utc...) to display the correct DateTime with the user offset/timezone
   - Converted to a timezone-aware DateTime of 'UTC' using pytz
   - Then converted .astimezone() to current_user.timezone with pytz (like qsos:edit part)

# Dates notes
 - When entering a QSO format is : DD-MM-YYYY HH:MM:SSSS (Two fields)
 - A Python DateTime is "YYYY MM DD HH:MM:SS" (approximately, order is ok)
 - In ADIF format is YYYYMMDD HHMMSS (Two fields)
 - When editing a QSO, the unique field is displayed as "YYYY-MM-DD HH:MM:SS"

# TODO
 - eQSL integration
 - HAMQTH integration
 - Radio/CAT edit, add you own rig and link them when QSOing

