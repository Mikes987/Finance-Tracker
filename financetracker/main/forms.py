from flask_wtf import FlaskForm
from wtforms import SelectField, SubmitField, StringField, DateField, DecimalField, ValidationError
from wtforms.validators import DataRequired
import sqlalchemy as sa
import decimal

class CreateViewForm(FlaskForm):
    currency = SelectField('Choose Currency', validators=[DataRequired()])
    submit = SubmitField('Create View')


class CreateCategoryForm(FlaskForm):
    type_field = SelectField('Choose Type', validators=[DataRequired()])
    category_field = StringField('Category', validators=[DataRequired()])
    submit = SubmitField('Create Category')


class TrackingForm(FlaskForm):
    date_field = DateField('Date', validators=[DataRequired()])
    type_field = SelectField('Choose Type', validators=[DataRequired()])
    category_field = SelectField('Choose Category', validators=[DataRequired()], validate_choice=False)
    amount_field = DecimalField('Amount', places=2, rounding=decimal.ROUND_HALF_UP, validators=[DataRequired()])
    goal_field = SelectField('Choose Source/Target', validators=[DataRequired()])
    comment_field = StringField('Comment', validators=[DataRequired()])
    submit_field = SubmitField('Submit')
    
    def validate_amount_field(self, amount_field):
        data = amount_field.data
        if abs(data.as_tuple().exponent) > 2:
            raise ValidationError("Please enter 2 decimals max.")