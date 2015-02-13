from flask import render_template, flash, redirect, session, url_for, request, g
from werkzeug.security import generate_password_hash, check_password_hash
from flask_login import login_user, logout_user, current_user, login_required
from app import app, db, lm
from forms import LoginForm, FeedbackForm
from models import User, Feedback, Applicant

@app.before_request
def before_request():
  g.user = current_user

@app.route('/home')
@login_required
def index():
  applicants = Applicant.query.all()
  context = {
    'title': 'Home',
    'applicants': applicants
  }
  template = 'index.html'
  if g.user.has_role('staff'):
    template = 'review.html'
  return render_template(template, **context)


@app.route('/', methods=['GET', 'POST'])
@app.route('/login', methods=['GET', 'POST'])
def login():
  if g.user is not None and g.user.is_authenticated():
    return redirect(url_for('index'))
  form = LoginForm()
  if form.validate_on_submit():
    user = User.query.filter_by(email=form.email.data).first()
    if user:
      if check_password_hash(user.password, form.password.data):
        login_user(user, remember=True)
        return redirect(request.args.get('next') or url_for('index'))
  return render_template('login.html', title='Sign In', form=form)

@app.route('/logout')
@login_required
def logout():
  logout_user()
  return redirect(url_for('login'))

@app.route('/feedback/<int:applicant_id>', methods=['GET', 'POST'])
@login_required
def applicant(applicant_id):
  feedback = Feedback.query.filter_by(user_id=g.user.id, applicant_id=applicant_id).first()
  if feedback:
    form = FeedbackForm(notes=feedback.notes, feedback=feedback.feedback)
  else:
    form = FeedbackForm()
  if form.validate_on_submit():
    if feedback:
      feedback.notes = form.notes.data
      feedback.feedback = form.feedback.data
    else:
      feedback = Feedback(user_id=g.user.id, applicant_id=applicant_id,
                          notes=form.notes.data, feedback=form.feedback.data)
    db.session.add(feedback)
    db.session.commit()
    return redirect(url_for('index'))

  applicant = Applicant.query.get(applicant_id)
  context = {
    'title': applicant.name,
    'applicant': applicant,
    'form': form
  }
  return render_template('applicant.html', **context)


@lm.user_loader
def load_user(id):
  return User.query.get(int(id))