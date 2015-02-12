from flask_wtf import Form
from wtforms import StringField, BooleanField, PasswordField, TextAreaField
from wtforms.validators import DataRequired, Length, Optional

class LoginForm(Form):
  email = StringField('email', validators=[DataRequired()])
  password = PasswordField('password', validators=[DataRequired()])
  # Length(min=5, max=120)
class FeedbackForm(Form):
  notes = TextAreaField('notes', validators=[Optional()])
  feedback = TextAreaField('feedback')
