import datetime
from libqth import is_valid_qth

from flask_security import RegisterForm, current_user
from flask_uploads import UploadSet, IMAGES
from flask_wtf import Form
from flask_wtf.file import FileField, FileAllowed, FileRequired
from wtforms import PasswordField, SubmitField, TextAreaField, SelectField, IntegerField, \
    HiddenField, BooleanField
from wtforms.ext.dateutil.fields import DateTimeField
from wtforms.ext.sqlalchemy.fields import QuerySelectField
from wtforms.validators import DataRequired, ValidationError, Optional
from wtforms_alchemy import model_form_factory
from wtforms_components.fields import SelectField as WTFComponentsSelectField
from wtforms import widgets
from wtforms.fields.core import StringField

from models import db, User, Note, Cat, Mode, Band, Logbook
from utils import dt_utc_to_user_tz

BaseModelForm = model_form_factory(Form)

pictures = UploadSet('pictures', IMAGES)


class PasswordFieldNotHidden(StringField):
    """
    Original source: https://github.com/wtforms/wtforms/blob/2.0.2/wtforms/fields/simple.py#L35-L42

    A StringField, except renders an ``<input type="password">``.
    Also, whatever value is accepted by this field is not rendered back
    to the browser like normal fields.
    """
    widget = widgets.PasswordInput(hide_value=False)


class ModelForm(BaseModelForm):
    @classmethod
    def get_session(cls):
        return db.session


class ExtendedRegisterForm(RegisterForm):
    name = StringField('Name', [DataRequired()])

    def validate_name(form, field):
        if len(field.data) <= 0:
            raise ValidationError("Username required")

        u = User.query.filter(User.name == field.data).first()
        if u:
            raise ValidationError("Username already taken")


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
    timezone = SelectField(coerce=str, label='Timezone', default='UTC')
    lotw_name = StringField('LoTW Username')
    lotw_password = PasswordFieldNotHidden('LoTW Password')
    eqsl_name = StringField('eQSL.cc Username')
    eqsl_password = PasswordFieldNotHidden('eQSL.cc Password')
    hamqth_name = StringField('HamQTH Username')
    hamqth_password = PasswordFieldNotHidden('HamQTH Password')

    swl = BooleanField('Are you a SWL HAM ?')

    zone = SelectField('Zone', choices=[['iaru1', 'IARU Zone 1'],
                                        ['iaru2', 'IARU Zone 2'],
                                        ['iaru3', 'IARU Zone 3']], validators=[DataRequired()])

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
    modes = {}
    q_modes = db.session.query(Mode.id, Mode.mode, Mode.submode).order_by(Mode.mode.asc()).all()
    for mode in q_modes:
        if mode.mode not in modes:
            modes[mode.mode] = []
        modes[mode.mode].append((mode.id, mode.submode))

    return list(sorted(modes.items()))


def get_bands():
    return Band.query.filter(Band.modes.is_(None),
                             Band.start.is_(None),
                             Band.zone == current_user.zone).order_by(Band.lower.asc()).all()


def dflt_mode():
    return str(Mode.query.filter(Mode.submode == 'LSB').first())


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


def get_logbooks():
    return Logbook.query.filter(Logbook.user_id == current_user.id).all()


class BaseQsoForm(Form):
    # Hardcoded value for mode default
    # WTFORMS-Components doesn't seems to be able to manage callable for default= unfortunately
    # We use 1 which should be the first Mode ID in database (LSB)
    call = StringField('Callsign', [DataRequired()])
    mode = WTFComponentsSelectField('Mode', choices=get_modes, validators=[DataRequired()], coerce=int, default='1')
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
    qsl_comment = StringField('QSL Comment')
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
    eqsl_qsl_sent = SelectField('eQSL Sent', choices=[['N', 'No'],
                                                      ['Y', 'Yes'],
                                                      ['R', 'Requested'],
                                                      ['Q', 'Queued'],
                                                      ['I', 'Invalid (Ignore)']])
    qsl_via = StringField('Via')

    submit = SubmitField('Save')


class QsoForm(BaseQsoForm):
    date = DateTimeField('Date', default=datetime.datetime.utcnow, display_format='%Y-%m-%d')
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
    logbook = QuerySelectField(query_factory=get_logbooks, allow_blank=False, label='Logbook', get_label='name')

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


class LogbookForm(Form):
    name = StringField('Name', [DataRequired()])
    callsign = StringField('Callsign', [DataRequired()])
    locator = StringField('Locator')

    def validate_gridsquare(form, field):
        if len(field.data) <= 2:
            raise ValidationError("QTH is too broad or empty, please input valid QTH")
        if not is_valid_qth(field.data, 6):
            raise ValidationError("QTH is invalid, validation failed")

    swl = BooleanField('Logbook of a SWL HAM ?')
    default = BooleanField('Do you want this logbook to be the default one ?')
    public = BooleanField('Make this logbook public ?')

    eqsl_qth_nickname = StringField('eQSL QTH Nickname')

    submit = SubmitField('Save logbook')


class PictureForm(Form):
    name = StringField('Name', [DataRequired()])
    picture = FileField('Image', [FileRequired(), FileAllowed(pictures, 'Images only!')])
    submit = SubmitField('Add picture')


class ConfigForm(Form):
    lotw_download_url = StringField('LOTW Download URL', [DataRequired()])
    lotw_upload_url = StringField('LOTW Upload URL', [DataRequired()])
    lotw_rcvd_mark = StringField('LOTW Rcvd Mark', [DataRequired()])
    lotw_login_url = StringField('LORW Login URL', [DataRequired()])
    eqsl_download_url = StringField('eQSL Download URL', [DataRequired()])
    eqsl_upload_url = StringField('eQSL Upload URL', [DataRequired()])
    eqsl_rcvd_mark = StringField('eQSL Rcvd Mark', [DataRequired()])
    clublog_api_key = StringField('ClubLog API Key')

    submit = SubmitField('Update config')


class AdvSearchForm(Form):
    # Remember that the Full Text Search already search text within:
    # Call, Comment, Country, Email, Name, Notes, Operator,
    # Owner callsign, Qslmsg, Station callsign, Web and Qsl comment

    # Select inputs will have a first field "Any" value "any"
    from_date = DateTimeField("From date", [Optional()])
    to_date = DateTimeField("To date", [Optional()])
    fts = StringField("Search string", [Optional()])
    country = SelectField(label='Country', validators=[Optional()])
    call = StringField("Callsign", [Optional()])
    mode = SelectField(label='Mode', validators=[Optional()])
    band = SelectField(label='Band', validators=[Optional()])
    frequency = IntegerField("Freq", [Optional()])
    pictures = SelectField(label='Has pictures', validators=[Optional()],
                           choices=[['any', 'Any'],
                                    ['Y', 'Yes'],
                                    ['N', 'No']])
    # qsl statues <select>
    # eqsl statues <select>
    # pictures <select>

    submit = SubmitField('Search')
