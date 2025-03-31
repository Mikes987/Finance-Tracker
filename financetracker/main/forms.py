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


class TrackingForm(FlaskForm):
    
    date_field = StringField('Date', validators=[DataRequired()])
    type_field = SelectField('Choose Type', validators=[DataRequired()])
    category_field = SelectField('Choose Category', validators=[DataRequired()], validate_choice=False)
    amount_field = StringField('Amount', validators=[DataRequired()])
    goal_field = SelectField('Choose Source/Target', validators=[DataRequired()])
    comment_field = StringField('Comment', validators=[DataRequired()])
    submit_field = SubmitField('Submit')