Another Ham Radio Log
=====================

# Versions requirement
 - Python >= 3.3 (3.0, 3.1, 3.2 not supported)

# Installation
    Install a BDD (sqlite, mysql, postgresql)
    Makes sure that encoding is/will be in UNICODE/UTF-8
    git clone http://dev.sigpipe.me/DashieHam/ahrl
    cd ahrl
    git submodule init
    git submodule update
    pip3 install --requirement requirements.txt  # if present
    pip3 install git+http://dev.sigpipe.me/DashieHam/pyHamQth.git
    cp config.py.sample config.py
    $EDITOR config.py
    python3 ahrl.py db upgrade
    python3 ahrl.py db seed
    python3 ahrl.py cron update_dxcc_from_cty
    python3 ahrl.py runserver # or whatever gunicorn whatever stuff
    Don't forget to update default Config by getting to "Your user" (top right) then "Config"

# Gunicorn
    gunicorn -w 2 -b 127.0.0.1:8000 --error-logfile=errors.log --access-logfile=access.log --chdir=$PWD ahrl:app

# Default config
 - LOTW Download URL: https://p1k.arrl.org/lotwuser/lotwreport.adi
 - LOTW Upload URL: https://p1k.arrl.org/lotwuser/upload
 - LOTW Rcvd Mark: 'Y'
 - LOTW Login URL: https://p1k.arrl.org/lotwuser/default
 - eQSL Download URL: https://www.eqsl.cc/qslcard/DownloadInBox.cfm
 - eQSL Upload URL: https://www.eqsl.cc/qslcard/ImportADIF.cfm
 - eQSL Rcvd Mark: 'Y'
 - Cloudlog API Key: You needs to get one (for the moment)

# Crontabs and cache actions
  List of cron target availables.
  Makes sure to run them under the user which runs ahrl and virtualenv if you use it.
  Commands:
  - python ahrl.py cron update_qsos_countries  # Update all QSOs if missing a Country/DXCC entry by using ClubLog
  - python ahrl.py cron  # List all available crons
  - python ahrl.py cache  # Same for cache actions

# Licensing
 - MIT License

# Fork from
 - This is majoritary a fork of https://github.com/magicbug/Cloudlog by 2E0SQL
 - Thanks to him for all his work on CloudLog which inspired me (and from which I reused some things)

# Random notes (since I am currently no licensed and then I am SWL at the moment)
 - Your user have a CALLSIGN, LOCATOR and IARU Zone
  - Each logbook can have a different LOCATOR or CALLSIGN
  - I see that more like to have a different logbook if you do SAT / GHZ / Portable / Mobile etc.
  - Or if you want to have a log for your home base, from some DX remote site, etc.
  - So the IARU Zone isn't a choice for logbook, they use user profile anyway
 - Any things can be subject to discussion anyway, if something isn't really ok, no problem to see what to do

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

# Modes and Submodes
 - They are based on ADIF ones (http://adif.org/304/ADIF_304.htm#Mode_Enumeration)
 - 'mode' is like a category and 'submode' the real mode used (anyway...)
 - SSB is 'category' and in fact you use 'USB' or 'LSB'
 - So in some places the keyword 'mode' is used but in fact it's really 'submode' which is used

# TODO
 - eQSL integration
 - HAMQTH integration
 - Radio/CAT edit, add you own rig and link them when QSOing

