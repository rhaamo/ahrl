Another Ham Radio Log
=====================



# Installation
    Install a BDD (sqlite, mysql, postgresql)
    Makes sure that encoding is/will be in UNICODE/UTF-8
    git clone http://dev.sigpipe.me/dashie/ahrl
    cd ahrl
    git submodule init
    git submodule update
    pip install --requirement requirements.txt
    cp config.py.sample config.py
    $EDITOR config.py
    python ahrl.py db upgrade
    python ahrl.py db_seed
    python ahrl.py mkdirs
    python ahrl.py runserver # or whatever gunicorn whatever stuff

# Gunicorn
    gunicorn -w 2 -b 127.0.0.1:8000 --error-logfile=errors.log --access-logfile=access.log --chdir=$PWD ahrl:app

# Crontabs
    TBD

# Licensing
 - MIT License

# TODO
 - Unicorns
 - More unicorns
 - Even more unicorns !

