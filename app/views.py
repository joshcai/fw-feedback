from flask import render_template, flash, redirect, session, url_for, request, g
from werkzeug.security import generate_password_hash, check_password_hash
from flask_login import login_user, logout_user, current_user, login_required
from app import app, db, lm
from forms import LoginForm
from models import User

@app.before_request
def before_request():
  g.user = current_user

@app.route('/')
@app.route('/index')
def index():
  return render_template('index.html', title='Home')

@app.route('/login', methods=['GET', 'POST'])
def login():
  if g.user is not None and g.user.is_authenticated():
    return redirect(url_for('index'))
  form = LoginForm()
  if form.validate_on_submit():
    user = User.query.get(form.email.data)
    if user:
      # if check_password_hash(user.password, form.password.data):
      login_user(user, remember=True)
      return redirect(url_for('index'))
  return render_template('login.html', title='Sign In', form=form)

@app.route('/logout')
@login_required
def logout():
    logout_user()
    return redirect(url_for('index'))

@lm.user_loader
def load_user(id):
    return User.query.get(int(id))