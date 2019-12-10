from flask_wtf import FlaskForm
from wtforms import SubmitField, TextAreaField, StringField
from flask_babel import lazy_gettext as _l
from wtforms.validators import DataRequired, length


class TipForm(FlaskForm):
    tip = TextAreaField(_l('Tip content'), validators=[DataRequired()])
    hashtags = StringField(_l('Hashtags'))
    submit = SubmitField(_l('Submit'))
