from flask_babel import lazy_gettext as _l
from flask_wtf import FlaskForm
from wtforms import SubmitField, TextAreaField, StringField
from wtforms.validators import DataRequired


class TipForm(FlaskForm):
    tip = TextAreaField(_l('Tip content'), validators=[DataRequired()])
    hashtags = StringField(_l('Hashtags'))
    submit = SubmitField(_l('Submit'))
