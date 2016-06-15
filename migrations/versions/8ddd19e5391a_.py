"""empty message

Revision ID: 8ddd19e5391a
Revises: 516077ddda8d
Create Date: 2016-06-15 11:38:25.620662

"""

# revision identifiers, used by Alembic.
revision = '8ddd19e5391a'
down_revision = '516077ddda8d'

from models import db, Mode


def upgrade():
    # 1/ Update existing modes
    ssb = Mode.query.filter(Mode.mode == 'SSB').one()
    ssb.submode = 'LSB'
    am = Mode.query.filter(Mode.mode == 'AM').one()
    am.submode = 'AM'
    fm = Mode.query.filter(Mode.mode == 'FM').one()
    fm.submode = 'FM'
    cw = Mode.query.filter(Mode.mode == 'CW').one()
    cw.submode = 'PCW'
    rtty = Mode.query.filter(Mode.mode == 'RTTY').one()
    rtty.submode = 'ASCII'
    psk31 = Mode.query.filter(Mode.mode == 'PSK31').one()
    psk31.mode = 'PSK'
    psk31.submode = 'PSK31'
    psk63 = Mode.query.filter(Mode.mode == 'PSK63').one()
    psk63.mode = 'PSK'
    psk63.submode = 'PSK63'
    sstv = Mode.query.filter(Mode.mode == 'SSTV').one()
    sstv.submode = 'SSTV'
    pkt = Mode.query.filter(Mode.mode == 'PKT').one()
    pkt.submode = 'PKT'
    for i in ['JT65', 'JT65B', 'JT6C', 'JT6M', 'JT9-1',
              'FSK441', 'JTMS', 'ISCAT']:
        db.session.delete(Mode.query.filter(Mode.mode == i).one())

    # 2/ Feed using ADIF Enumerations
    modes = {
        'ATV': ['ATV'],
        'CHIP': ['CHIP64', 'CHIP128'],
        'CLO': ['CLO'],
        'CONTESTI': ['CONTESTI'],
        'DIGITALVOICE': ['DIGITALVOICE'],
        'DOMINO': ['DOMINOEX', 'DOMINOF'],
        'DSTAR': ['DSTAR'],
        'FAX': ['FAX'],
        'FSK441': ['FSK441'],
        'HELL': ['FMHELL', 'FSKHELL', 'HELL80', 'HFSK', 'PSKHELL'],
        'ISCAT': ['ISCAT-A', 'ISCAT-B'],
        'JT4': ['JT4A', 'JT4B', 'JT4C', 'JT4D', 'JT4E', 'JT4F', 'JT4G'],
        'JT6M': ['JT6M'],
        'JT9': ['JT9-1', 'JT9-2', 'JT9-5', 'JT9-10', 'JT9-30'],
        'JT44': ['JT44'],
        'JT65': ['JT65A', 'JT65B', 'JT65B2', 'JT65C', 'JT65C2'],
        'MFSK': ['MFSK4', 'MFSK8', 'MFSK11', 'MFSK16', 'MFSK22', 'MFSK31', 'MFSK32', 'MFSK64', 'MFSK128'],
        'MT63': ['MT63'],
        'OLIVIA': ['OLIVIA 4/125', 'OLIVIA 4/250', 'OLIVIA 8/250', 'OLIVIA 8/500', 'OLIVIA 16/500',
                   'OLIVIA 16/1000', 'OLIVIA 32/1000'],
        'OPERA': ['OPERA-BEACON', 'OPERA-QSO'],
        'PAC': ['PAC2', 'PAC3', 'PAC4'],
        'PAX': ['PAX2'],
        'PKT': ['PKT'],
        'PSK': ['FSK31', 'PSK10', 'PSK63F', 'PSK125', 'PSK250', 'PSK500', 'PSK1000',
                'PSKAM10', 'PSKAM31', 'PSKAM50', 'PSKFEC31', 'QPSK31', 'QPSK63', 'QPSK125', 'QPSK250', 'QPSK500'],
        'PSK2K': ['PSK2K'],
        'Q15': ['Q15'],
        'ROS': ['ROS-EME', 'ROS-HF', 'ROS-MF'],
        'RTTYM': ['RTTYM'],
        'SSB': ['USB'],
        'THOR': ['THOR'],
        'THRB': ['THRBX'],
        'TOR': ['AMTORFEC', 'GTOR'],
        'V4': ['V4'],
        'VOI': ['VOI'],
        'WINMOR': ['WINMOR'],
        'WSPR': ['WSPR']
    }

    for mode in modes.keys():
        for submode in modes[mode]:
            db.session.add(Mode(mode=mode, submode=submode))

    db.session.commit()


def downgrade():
    pass
