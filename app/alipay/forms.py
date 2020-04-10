from flask_wtf import FlaskForm
from wtforms import StringField, SubmitField, TextAreaField
from wtforms.validators import  DataRequired
from flask_babel import lazy_gettext as _l


class queryorderform(FlaskForm):
    order_number = StringField(_l('order'), validators=[DataRequired()])
    submit = SubmitField(_l('Query'))
