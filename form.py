from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, SubmitField, BooleanField, TextAreaField
from wtforms.validators import DataRequired, Length, Email, EqualTo
from wtforms.fields.html5 import DateField
import datetime

class RegistrationForm(FlaskForm):
	
	username = StringField('Username', validators = [DataRequired(), Length(min = 2, max = 20)])
	email = StringField('Email', validators = [DataRequired(), Email()])
	password = PasswordField('Password', validators = [DataRequired()])
	confirm_password = PasswordField('Confirm Password', validators = [DataRequired(), EqualTo('password')])
	submit = SubmitField('Sign Up')

class LoginForm(FlaskForm):
	
	email = StringField('Email', validators = [DataRequired(), Email()])
	password = PasswordField('Password', validators = [DataRequired()])
	remember = BooleanField('Remember me')
	submit = SubmitField('Login')

class NERForm(FlaskForm):

	date_field = DateField('Enter the date', format = '%Y-%m-%d', default = datetime.date.today())
	text_area = TextAreaField("Enter crime query", validators = [DataRequired()])
	submit = SubmitField('Extract')

class ForgotPassword(FlaskForm):

	email = StringField('Enter your email', validators = [DataRequired(), Email()])
	submit = SubmitField('Submit')

class ResetPassword(FlaskForm):

	reset = StringField('Enter reset code', validators = [DataRequired()])
	password = PasswordField('New Password', validators = [DataRequired()])
	confirm_password = PasswordField('Confirm Password', validators = [DataRequired(), EqualTo('password')])
	submit = SubmitField('Submit')