from flask_wtf import FlaskForm
from wtforms import SelectField, SubmitField, StringField
from wtforms.validators import DataRequired
import sqlalchemy as sa

class CreateViewForm(FlaskForm):
    currency = SelectField('Choose Currency', validators=[DataRequired()])
    submit = SubmitField('Create View')


class CreateCategoryForm(FlaskForm):
    type_field = SelectField('Choose Type', validators=[DataRequired()])
    category_field = StringField('Category', validators=[DataRequired()])
    submit = SubmitField('Create Category')