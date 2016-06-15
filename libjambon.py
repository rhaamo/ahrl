import math
from models import Band, Mode
from sqlalchemy import or_


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
                            Band.upper > f).single()
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
