from flask_wtf import Form
from wtforms import StringField, PasswordField, SubmitField, TextAreaField, SelectField, IntegerField, \
    HiddenField, BooleanField
from flask_wtf.file import FileField, FileAllowed, FileRequired
from wtforms.validators import DataRequired, ValidationError
from flask_security import RegisterForm
from models import db, User, Note, Cat, Mode, Band
from wtforms_alchemy import model_form_factory
from wtforms.ext.sqlalchemy.fields import QuerySelectField
from wtforms.ext.dateutil.fields import DateTimeField
from utils import dt_utc_to_user_tz
from libqth import is_valid_qth
import datetime
import pytz

BaseModelForm = model_form_factory(Form)


class ModelForm(BaseModelForm):
    @classmethod
    def get_session(cls):
        return db.session


class ExtendedRegisterForm(RegisterForm):
    name = StringField('Name', [DataRequired()])


class UserProfileForm(ModelForm):
    class Meta:
        model = User

    password = PasswordField('Password')
    name = StringField('Name')
    email = StringField('Email')

    callsign = StringField('Callsign', [DataRequired()])

    locator = StringField('Locator', [DataRequired()])
    
    def validate_locator(form, field):
        if len(field.data) <= 2:
            raise ValidationError("QTH is too broad, please input valid QTH")
        if not is_valid_qth(field.data, 6):
            raise ValidationError("QTH is invalid, validation failed")

    firstname = StringField('Firstname')
    lastname = StringField('Lastname')
    timezone = SelectField(choices=zip(pytz.all_timezones, pytz.all_timezones),
                           label='Timezone', default='UTC')
    lotw_name = StringField('LoTW Username')
    lotw_password = PasswordField('LoTW Password')
    eqsl_name = StringField('eQSL.cc Username')
    eqsl_password = PasswordField('eQSL.cc Password')

    swl = BooleanField('Are you a SWL HAM ?')

    submit = SubmitField('Update profile')


class NoteForm(ModelForm):
    class Meta:
        model = Note

    cat = SelectField(choices=[
        ('General', 'General'),
        ('Antennas', 'Antennas'),
        ('Satellites', 'Satellites')], default=['General'], label='Category')
    title = StringField('Title', [DataRequired()])
    note = TextAreaField('Note', [DataRequired()])

    submit = SubmitField('Sauver note')


def get_modes():
    return Mode.query.all()


def get_bands():
    return Band.query.filter(Band.modes.is_(None), Band.start.is_(None)).all()


def dflt_mode():
    return Mode.query.filter(Mode.mode == 'SSB').first()


def dflt_band():
    return Band.query.filter(Band.modes.is_(None), Band.start.is_(None), Band.name == '40m').first()


list_of_props = [['', ''], ['AUR', 'Aurora'], ['AUE', 'Aurora-E'], ['BS', 'Back scatter'],
                 ['ECH', 'EchoLink'], ['EME', 'Earth-Moon-Earth'], ['ES', 'Sporadic E'],
                 ['FAI', 'Field Aligned Irregularities'], ['F2', 'F2 Reflection'],
                 ['INTERNET', 'Internet-assisted'], ['ION', 'Ionoscatter'], ['IRL', 'IRLP'],
                 ['MS', 'Meteor scatter'], ['RPT', 'Terrestrial or atmospheric repeater or transponder'],
                 ['RS', 'Rain scatter'], ['SAT', 'Satellite'], ['TEP', 'Trans-equatorial'],
                 ['TR', 'Tropospheric ducting']]


def get_radios():
    return Cat.query.all()


def foo_bar_baz_qux():
    return dt_utc_to_user_tz(datetime.datetime.utcnow())


class BaseQsoForm(Form):
    call = StringField('Callsign', [DataRequired()])
    mode = QuerySelectField(query_factory=get_modes, default=dflt_mode, label='Mode',
                            validators=[DataRequired()], get_label='mode')
    band = QuerySelectField(query_factory=get_bands, default=dflt_band, label='Band',
                            validators=[DataRequired()], get_label='name')
    rst_sent = IntegerField('RST (S)', [DataRequired()], default=59)
    rst_rcvd = IntegerField('RST (R)', [DataRequired()], default=59)
    name = StringField('Name')
    qth = StringField('Location')

    gridsquare = StringField('Locator')

    def validate_gridsquare(form, field):
        if len(field.data) <= 0:
            return  # ignore if no QTH entered

        if len(field.data) <= 2:
            raise ValidationError("QTH is too broad, please input valid QTH")
        if not is_valid_qth(field.data, 6):
            raise ValidationError("QTH is invalid, validation failed")

    comment = StringField('Comment')
    country = StringField('Country', [DataRequired()])

    web = StringField('URL')

    # Hidden
    dxcc = HiddenField(validators=[DataRequired()])
    cqz = HiddenField(validators=[DataRequired()])

    # Home
    prop_mode = SelectField(choices=list_of_props, default='', label='Propagation Mode')
    iota = StringField('IOTA')

    # Station
    radio = QuerySelectField(query_factory=get_radios, allow_blank=True, label='Radio', get_label='radio')
    freq = IntegerField('Frequency', [DataRequired()])

    # Satellite
    sat_name = StringField('Sat name')
    sat_mode = StringField('Sat mode')

    # QSL
    qsl_sent = SelectField('QSL Sent', choices=[['N', 'No'],
                                                ['Y', 'Yes'],
                                                ['R', 'Requested'],
                                                ['Q', 'Queued'],
                                                ['I', 'Invalid (Ignore)']])
    qsl_sent_via = SelectField('Sent via', choices=[['', 'Method'],
                                                    ['D', 'Direct'],
                                                    ['B', 'Bureau'],
                                                    ['E', 'Electronic'],
                                                    ['M', 'Manager']])
    qsl_via = StringField('Via')

    submit = SubmitField('Save')


class QsoForm(BaseQsoForm):
    date = DateTimeField('Date', default=datetime.datetime.utcnow, display_format='%d-%m-%Y')
    time = DateTimeField('Time', default=foo_bar_baz_qux, display_format='%H:%M:%S')


class EditQsoForm(BaseQsoForm):
    time_on = DateTimeField('Start date', display_format='%Y-%m-%d %H:%M:%S', validators=[DataRequired()])
    time_off = DateTimeField('End date', display_format='%Y-%m-%d %H:%M:%S', validators=[DataRequired()])
    notes = TextAreaField('Notes')

    qsl_rcvd = SelectField('QSL Received', choices=[['N', 'No'],
                                                    ['Y', 'Yes'],
                                                    ['R', 'Requested'],
                                                    ['I', 'Invalid (Ignore)'],
                                                    ['V', 'Verified (Match)']])

    qsl_rcvd_via = SelectField('Received via', choices=[['', 'Method'],
                                                        ['D', 'Direct'],
                                                        ['B', 'Bureau'],
                                                        ['E', 'Electronic'],
                                                        ['M', 'Manager']])

    eqsl_qsl_rcvd = SelectField('eQSL Received', choices=[['N', 'No'],
                                                          ['Y', 'Yes'],
                                                          ['R', 'Requested'],
                                                          ['I', 'Invalid (Ignore)'],
                                                          ['V', 'Verified (Match)']])

    eqsl_qsl_sent = SelectField('eQSL Sent', choices=[['N', 'No'],
                                                      ['Y', 'Yes'],
                                                      ['R', 'Requested'],
                                                      ['Q', 'Queued'],
                                                      ['I', 'Invalid (Ignore)']])

    lotw_qsl_rcvd = SelectField('LOTW QSL Received', choices=[['N', 'No'],
                                                              ['Y', 'Yes'],
                                                              ['R', 'Requested'],
                                                              ['I', 'Invalid (Ignore)'],
                                                              ['V', 'Verified (Match)']])

    lotw_qsl_sent = SelectField('LOTW QSL Sent', choices=[['N', 'No'],
                                                          ['Y', 'Yes'],
                                                          ['R', 'Requested'],
                                                          ['Q', 'Queued'],
                                                          ['I', 'Invalid (Ignore)']])


class AdifParse(Form):
    adif_file = FileField('File', [FileRequired(),
                                   FileAllowed(['adi', 'adif'], 'Adif only !')])
    submit = SubmitField('Import file')


class FilterLogbookBandMode(Form):
    mode = SelectField(label='Mode', validators=[DataRequired()])
    band = SelectField(label='Band', validators=[DataRequired()])
    submit = SubmitField('Filter')


class ContactsForm(Form):
    callsign = StringField('Callsign', [DataRequired()])
    gridsquare = StringField('Locator')

    def validate_gridsquare(form, field):
        if len(field.data) <= 2:
            raise ValidationError("QTH is too broad or empty, please input valid QTH")
        if not is_valid_qth(field.data, 6):
            raise ValidationError("QTH is invalid, validation failed")

    submit = SubmitField('Save contact')