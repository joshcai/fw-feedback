from flask_wtf import Form
from wtforms import StringField, BooleanField, PasswordField, TextAreaField, RadioField, SelectMultipleField, widgets
from wtforms.validators import DataRequired, Length, Optional, EqualTo

class MultiCheckboxField(SelectMultipleField):
  widget = widgets.ListWidget(prefix_label=False)
  option_widget = widgets.CheckboxInput()

class LoginForm(Form):
  email = StringField('email', validators=[DataRequired()])
  password = PasswordField('password', validators=[DataRequired()])

class FeedbackForm(Form):
  notes = TextAreaField('notes', validators=[Optional()])
  feedback = TextAreaField('feedback')
  rating = RadioField('rating', choices=[('None', 'None'), ('1', '1'), ('2', '2'), ('3', '3'),
                      ('4', '4'), ('5', '5 (best)')], validators=[Optional()])

class PasswordForm(Form):
  password = PasswordField('password',
      validators=[DataRequired(), Length(min=5, max=30), EqualTo('confirm', message='Passwords must match')])
  confirm = PasswordField('password_confirm')

class FilterForm(Form):
  sort = RadioField('sort', choices=[('last', 'Last Name'), ('first', 'First Name'),
      ('most', 'Most Feedback'), ('least', 'Least Feedback')])
  groups = MultiCheckboxField('groups', choices=[('1', 'Group 1'), ('2', 'Group 2'),
      ('3', 'Group 3'), ('4', 'Group 4')])
  gender = MultiCheckboxField('gender', choices=[('m', 'Male'), ('f', 'Female')])
  location = MultiCheckboxField('location', choices=[('texas', 'Texas'), ('other', 'Other')])
  interaction = MultiCheckboxField('interaction', choices=[('yes', 'Reviewed'),
    ('no', 'Not Reviewed')])

class ForgotForm(Form):
  email = StringField('email', validators=[DataRequired()])

class AddUserForm(Form):
  email = StringField('email', validators=[DataRequired()])
  name = StringField('name', validators=[DataRequired()])
  roles = RadioField('roles', choices=[('other', 'Other'),
    ('senior', 'Senior'), ('alumni', 'Alumni'), ('staff', 'Staff')])