Another Ham Radio Log
=====================

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

# TODO
 - eQSL integration
 - HAMQTH integration
 - QSO edit
 - More statistics
 - Radio/CAT edit, add you own rig and link them when QSOing

