import math
from models import Band, Mode
from sqlalchemy import or_
import urllib.request
import bs4 as BeautifulSoup
import re


def band_to_frequency(band, mode):
    if not isinstance(band, int) or not isinstance(mode, int):
        raise TypeError('Sorry but only integer')

    b = Band.query.filter(Band.id == band).first()
    m = Mode.query.filter(Mode.id == mode).first()

    if not b or not m:
        return None

    frequencies = Band.query.filter(Band.lower.is_(None),
                                    Band.upper.is_(None),
                                    Band.name == b.name,
                                    or_(Band.modes.contains(m.submode),
                                        Band.modes.contains(m.mode)))

    if frequencies.count() <= 0:
        return b.lower
    else:
        return frequencies.first().start


def frequency_to_band(frequency, zone='iaru1'):
    f = frequency
    if type(f) == str:
        f = int(frequency)

    f_q = Band.query.filter(Band.start.is_(None),
                            Band.lower < f,
                            Band.upper > f,
                            Band.zone == zone).single()
    return f_q.name


def geo_bearing_star(bearing):
    dirs = ['N', 'E', 'S', 'W']

    rounded = round(bearing / 22.5) % 16
    if (rounded % 4) == 0:
        _dir = dirs[int(rounded / 4)]
    else:
        _dir = dirs[int(2 * math.floor(((math.floor(rounded / 4) + 1) % 4) / 2))]
        _dir += dirs[int(1 + 2 * math.floor(rounded / 8))]
    return _dir


def adif(k, v):
    v = str(v)
    return u"<{0}:{1}>{2} ".format(k.upper(), len(v), v)


def eqsl_upload_log(log, config):
    """ Doc: https://www.eqsl.cc/qslcard/ImportADIF.txt """
    reject = False
    # Sanity check
    if not config.eqsl_download_url:
        return {'state': 'error', 'message': 'config.eqsl_download_url empty'}
    if not log.user.eqsl_name:
        return {'state': 'error', 'message': 'user.eqsl_name empty'}
    if not log.user.eqsl_password:
        return {'state': 'error', 'message': 'user.eqsl_password empty'}
    if not log.call:
        return {'state': 'error', 'message': 'log.call empty'}
    if not log.band:
        return {'state': 'error', 'message': 'log.band empty'}
    if not log.mode:
        return {'state': 'error', 'message': 'log.mode empty'}
    if not log.time_on:
        return {'state': 'error', 'message': 'log.time_on empty'}
    if not log.rst_sent:
        return {'state': 'error', 'message': 'log.rst_sent empty'}
    # End of checks
    # Build URL
    url = config.eqsl_upload_url
    log_adif = "AHRL Upload"
    log_adif += adif('adif_ver', '1.00') + ' \r\n'
    # Test
    #log_adif += adif('eqsl_user', 'TEST-SWL') + ' '
    #log_adif += adif('eqsl_pswd', 'Testpswd') + ' '
    # Real ones
    log_adif += adif('eqsl_user', log.user.eqsl_name) + ' '
    log_adif += adif('eqsl_pswd', log.user.eqsl_password) + ' '
    log_adif += '<EOH> '
    log_adif += adif('band', log.band.name.upper()) + ' \r\n'
    log_adif += adif('call', 'TEST-SWL') + ' '

    # eQSL Mode standardization (http://www.eqsl.cc/qslcard/ADIFContentSpecs.cfm)
    if log.mode.mode == 'OLIVIA':
        mode = 'OLIVIA'
    elif log.mode.submode == 'PAC4':
        mode = 'PAC'
    elif log.mode.submode in ['PSK250', 'PSK500', 'PSK1000', 'QPSK250', 'QPSK500', 'PSK2K', 'FSKHELL']:
        reject = True
    elif log.mode.mode == 'JT9':
        mode = 'JT9'
    elif log.mode.mode == 'JT65':
        mode = 'JT65'
    elif log.mode.mode == 'ISCAT':
        mode = 'ISCAT'
    elif log.mode.submode == 'USB' or log.mode.submode == 'LSB':
        mode = 'SSB'
    elif log.mode.mode == 'ROS':
        mode = 'ROS'
    elif log.mode.submode == 'DOMINOEX':
        mode = 'DOMINO'
    elif log.mode.mode == 'OPERA':
        mode = 'OPERA'
    elif log.mode.submode in ['MFSK4', 'MFSK11', 'MFSK22', 'MFSK31', 'MFSK32', 'MFSK64', 'MFSK128']:
        reject = True
    else:
        mode = log.mode.submode

    if reject:
        # Theses are modes not managed by eQSL, sorry
        return {'state': 'rejected',
                'message':'rejected because mode {0} not managed by eQSL'.format(log.mode.submode)}

    log_adif += adif('mode', mode.upper()) + ' '

    log_adif += adif('qso_date', log.time_on.strftime('%Y%m%d')) + ' '
    log_adif += adif('rst_sent', log.rst_sent) + ' '
    log_adif += adif('time_on', log.time_on.strftime('%H%M%S')) + ' \r\n'
    if log.qsl_comment:
        log_adif += adif('qslmsg', log.qsl_comment) + ' '
    log_adif += '<EOR>'

    try:
        data = urllib.parse.urlencode({'ADIFData': log_adif})
        data = data.encode('utf-8')
        req = urllib.request.Request(url, data)
        resp = urllib.request.urlopen(req)
    except ValueError as e:
        return {'state': 'error', 'message': str(e)}
    except urllib.error.URLError as e:
        return {'state': 'error', 'message': str(e)}

    soup = BeautifulSoup.BeautifulSoup(resp.read(), 'html.parser')

    body = soup.body.get_text().strip()

    # print(body)

    # Possible: 'Result', 'Warning', 'Error'
    rejected = False
    keys = []
    results = []
    for result in body.split('\r\n'):
        if result.strip() == '' or not result.strip():
            continue  # Ignore empty lines
        obj = re.match(r'^(.*): (.*)?', result.strip())
        results.append([obj.group(1), obj.group(2)])
        keys.append(obj.group(1))
        if obj.group(2) == '0 out of 1 records added' or obj.group(1) == 'Error':
            rejected = True

    if not rejected:
        return {'state': 'success', 'message': 'QSO Sync-ed to eQSL', 'msgs': results}
    else:
        return {'state': 'error', 'message': 'Some errors where detected', 'msgs': results}