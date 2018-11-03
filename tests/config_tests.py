# Website translations
BABEL_DEFAULT_LOCALE = "en"

# Paginations
# TBD later

# Lookup method for callsigns infos, available : [hamqth]
LOOKUP_METHOD = "hamqth"

# For QRZ integration
QRZ_USERNAME = ""
QRZ_PASSWORD = ""

# Uploads dirs
UPLOADED_PICTURES_DEST = "/home/dashie/dev/ahrl/uploads/pictures"
UPLOADS_DEFAULT_DEST = "/home/dashie/dev/ahrl/uploads"
TEMP_DOWNLOAD_FOLDER = "/home/dashie/dev/ahrl/tmp"

# If using sentry, set a DSN
SENTRY_USER_ATTRS = ["name", "email"]
SENTRY_DSN = ""

# Domain serving this app
AP_DOMAIN = "localhost"
BASE_URL = f"https://{AP_DOMAIN}"

# You can use a PostgreSQL database
SQLALCHEMY_DATABASE_URI = "postgresql+psycopg2://postgres@database:5432/ahrl_test"
# Or MySQL (at your own risks)
# SQLALCHEMY_DATABASE_URI = 'mysql://user:pass@host/ahrl'
# Or Maybe SQLite3 (at your own risks)
# SQLALCHEMY_DATABASE_URI = 'sqlite:///ahrl.db'

# Should users confirm theire email address ?
SECURITY_CONFIRMABLE = False
# Can users register on this instance ?
SECURITY_REGISTERABLE = True
# Can users recover theire password ?
SECURITY_RECOVERABLE = True
# Salt used for password hashing
# Do not change after users have registered
SECURITY_PASSWORD_SALT = "awooo"
# Do not change after users have registered
SECRET_KEY = "ahahahahahahahahahaquack"

# Mail setup
MAIL_SERVER = "localhost"
MAIL_PORT = 25
MAIL_USE_TLS = False
MAIL_USE_SSL = False
MAIL_USERNAME = None
MAIL_PASSWORD = None
MAIL_DEFAULT_SENDER = f"postmaster@{AP_DOMAIN}"

# Development only options
DEBUG = True
# We are testing
TESTING = True
SQLALCHEMY_ECHO = False
DEBUG_TB_PROFILER_ENABLED = False
DEBUG_TB_INTERCEPT_REDIRECTS = False

# Disable CSRF tokens in the Forms (only valid for testing purposes!)
WTF_CSRF_ENABLED = False

# Bcrypt algorithm hashing rounds (reduced for testing purposes only!)
BCRYPT_LOG_ROUNDS = 4

# Do not touch that
SQLALCHEMY_TRACK_MODIFICATIONS = False
SQLALCHEMY_RECORD_QUERIES = True
# Users can change password
# Do not disable, will breaks things
SECURITY_CHANGEABLE = True
# Password hash algorithm
SECURITY_PASSWORD_HASH = "bcrypt"
BABEL_DEFAULT_TIMEZONE = "UTC"


SECURITY_SEND_REGISTER_EMAIL = False
SECURITY_SEND_PASSWORD_CHANGE_EMAIL = False
SECURITY_SEND_PASSWORD_RESET_NOTICE_EMAIL = False

BOOTSTRAP_USE_MINIFIED = True
BOOTSTRAP_SERVE_LOCAL = True
BOOTSTRAP_CDN_FORCE_SSL = True
BOOTSTRAP_QUERYSTRING_REVVING = True
