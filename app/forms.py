from flask_wtf import Form
from wtforms import StringField, BooleanField, PasswordField, TextAreaField, RadioField
from wtforms.validators import DataRequired, Length, Optional, EqualTo

class LoginForm(Form):
  email = StringField('email', validators=[DataRequired()])
  password = PasswordField('password', validators=[DataRequired()])
  # Length(min=5, max=120)
class FeedbackForm(Form):
  notes = TextAreaField('notes', validators=[Optional()])
  feedback = TextAreaField('feedback')
  rating = RadioField('rating', choices=[('1', '1'), ('2', '2'), ('3', '3'),
                      ('4', '4'), ('5', '5 (best)')], validators=[Optional()])

class PasswordForm(Form):
  password = PasswordField('password', 
      validators=[DataRequired(), Length(min=5, max=30), EqualTo('confirm', message='Passwords must match')])
  confirm = PasswordField('password_confirm')

