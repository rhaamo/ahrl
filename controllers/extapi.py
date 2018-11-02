from flask import Blueprint, request, Response
from xmlrpc.server import CGIXMLRPCRequestHandler, SimpleXMLRPCDispatcher
from adif import parse as adif_parser
from models import db, Log, Band, Mode

bp_extapi = Blueprint("bp_extapi", __name__)

handler = SimpleXMLRPCDispatcher(allow_none=True, encoding=None)

"""
Register the XML-RPC introspection functions system.listMethods, system.methodHelp and system.methodSignature.
"""
handler.register_introspection_functions()

"""
<value>log.add_record</value>       log.add_record ADIF RECORD
<value>log.check_dup</value>        log.check_dup CALL, MODE(0), TIME_SPAN (0), FREQ_HZ(0), STATE(0), XCHG_IN(0)
<value>log.get_record</value>       log.get_record CALL
"""


def add_record(adif_record):
    print("Log.add_record")
    # FLDIGI send only a record, add fake end-of-header to not break parser
    parsed = adif_parser(b"<eoh>" + adif_record.encode("UTF-8"))
    if len(parsed) >= 1:
        parsed = parsed[0]
    """
    freq in MHz, time_off HHMMSS, qso_date YYYYMMDD, qso_date_off time_on same
    {'freq': '14.070997', 'mode': 'PSK31', 'time_off': '152417', 'qso_date': '20160824',
    'call': 'F4TEST', 'qso_date_off': '20160824', 'time_on': '1503'}
    """
    return "xxx"


def check_dup(call, mode, time_spam, freq_hz, state, xchg_in):
    print("Log.check_dup")
    return "xxx"


def get_record(call):
    print("Log.get_record")
    return "xxx"


handler.register_function(add_record, name="log.add_record")
handler.register_function(check_dup, name="log.check_dup")
handler.register_function(get_record, name="log.get_record")


@bp_extapi.route("/extapi/<path:whatever>", methods=["POST", "GET"])
def catchall(whatever):
    print("You wanted: {0}".format(whatever))


@bp_extapi.route("/extapi/RPC2", methods=["POST", "GET"])
def endpoint():
    dispatch = getattr(handler, "_dispatch", None)
    req = handler._marshaled_dispatch(request.data, dispatch)
    return Response(req, mimetype="text/xml")
