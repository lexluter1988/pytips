from flask_wtf import FlaskForm
from wtforms import SubmitField, TextAreaField
from flask_babel import lazy_gettext as _l
from wtforms.validators import DataRequired


class TipForm(FlaskForm):
    tip = TextAreaField(_l('Tip content'), validators=[DataRequired()])
    hashtags = TextAreaField(_l('Hashtags'), validators=[DataRequired()])
    submit = SubmitField(_l('Submit'))
