from flask import render_template, flash, redirect, session, url_for, request, g, send_file
from werkzeug.security import generate_password_hash, check_password_hash
from flask_login import login_user, logout_user, current_user, login_required
from app import app, db, lm
from forms import LoginForm, FeedbackForm
from models import User, Feedback, Applicant
from decorators import role_required
from tempfile import NamedTemporaryFile
from xlwt import Workbook

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

@app.route('/export')
@login_required
@role_required('staff')
def export():
  applicants = Applicant.query.order_by(Applicant.last_name).all()
  book = Workbook()
  sheet1 = book.add_sheet('Sheet 1')
  sheet1.write(0, 0, 'Finalists')
  sheet1.write(0, 1, 'Freshman-Juniors Average')
  sheet1.write(0, 2, 'Seniors Average')
  sheet1.write(0, 3, 'Alumni Average')
  for i, applicant in enumerate(applicants):
    sheet1.write(i+1, 0, '%s, %s' % (applicant.last_name, applicant.first_name))
    sheet1.write(i+1, 1, applicant.calculate_average('other'))
    sheet1.write(i+1, 2, applicant.calculate_average('senior'))
    sheet1.write(i+1, 3, applicant.calculate_average('alumni'))
  with NamedTemporaryFile() as f:
    book.save(f)
    f.seek(0)
    return send_file(f.name, as_attachment=True, attachment_filename='ratings.xls')


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
    form = FeedbackForm(notes=feedback.notes, feedback=feedback.feedback,
                        rating=feedback.rating)
  else:
    form = FeedbackForm()
  if form.validate_on_submit():
    if not feedback:
      feedback = Feedback(user_id=g.user.id, applicant_id=applicant_id)
    feedback.notes = form.notes.data
    feedback.feedback = form.feedback.data
    feedback.rating = form.rating.data
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