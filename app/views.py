from flask import render_template, flash, redirect, session, url_for, request, g, send_file
from werkzeug.security import generate_password_hash, check_password_hash
from flask_login import login_user, logout_user, current_user, login_required
from app import app, db, lm
from forms import LoginForm, FeedbackForm, FilterForm
from models import User, Feedback, Applicant
from decorators import role_required
from tempfile import NamedTemporaryFile
from xlwt import Workbook
from itsdangerous import URLSafeTimedSerializer
from emails import password_reset_email
from sqlalchemy import or_

ts = URLSafeTimedSerializer(app.config['SECRET_KEY'])

@app.before_request
def before_request():
  g.user = current_user

@app.route('/home', methods=['GET', 'POST'])
@login_required
def index():
  sort = 'last'
  groups = ['1', '2', '3', '4']
  gender = ['m', 'f']
  location = ['texas', 'other']
  form = FilterForm(sort=sort, groups=groups, gender=gender, location=location)
  applicants = Applicant.query
  if form.validate_on_submit():
    sort = form.sort.data
    groups = form.groups.data
    gender = form.gender.data
    location = form.location.data
  if sort == 'first':
    applicants = applicants.order_by(Applicant.first_name)
  elif sort == 'last':
    applicants = applicants.order_by(Applicant.last_name)
  if request.method == 'POST':
    group_clauses = []
    if '1' in groups:
      group_clauses.append(Applicant.group == '1')
    if '2' in groups:
      group_clauses.append(Applicant.group == '2')
    if '3' in groups:
      group_clauses.append(Applicant.group == '3')
    if '4' in groups:
      group_clauses.append(Applicant.group == '4')
    applicants = applicants.filter(or_(*group_clauses))
    gender_clauses = []
    if 'm' in gender:
      gender_clauses.append(Applicant.title == 'Mr.')
    if 'f' in gender:
      gender_clauses.append(Applicant.title == 'Ms.')
    applicants = applicants.filter(or_(*gender_clauses))
    location_clauses = []
    if 'texas' in location:
      location_clauses.append(Applicant.home_state == 'Texas')
    if 'other' in location:
      location_clauses.append(Applicant.home_state != 'Texas')
    applicants = applicants.filter(or_(*location_clauses))

  applicants = applicants.all()
  if sort == 'least':
    applicants = sorted(applicants, key=lambda x: x.feedback_count)
  elif sort == 'most':
    applicants = sorted(applicants, key=lambda x: x.feedback_count, reverse=True)
  template = 'index.html'
  if g.user.has_role('staff'):
    template = 'review.html'
  context = {
    'title': 'Home',
    'applicants': applicants,
    'form': form
  }
  return render_template(template, **context)

@app.route('/sendreset/<int:user_id>')
@login_required
@role_required('admin')
def send_activation_email(user_id):
  user = User.query.get(user_id)
  token = ts.dumps(user.email, salt='email-confirm-yay')
  url = url_for('reset_password', token=token, _external=True)
  password_reset_email(user, url)
  return 200
 
# Not finished
@app.route('/reset/<token>')
def password_reset(token):
  try:
    email = ts.loads(token, salt='email-confirm-yay', max_age=86400)
  except:
    abort(404)
  user = User.query.filter_by(email=email).first()

  login_user(user, remember=True)
  return 200
 
@app.route('/export')
@login_required
@role_required('staff')
def export():
  applicants = Applicant.query.order_by(Applicant.last_name).all()
  book = Workbook()
  sheet1 = book.add_sheet('Rating Averages')
  sheet2 = book.add_sheet('Ratings');
  sheet1.write(0, 0, 'Finalists')
  sheet1.write(0, 1, 'Freshman-Juniors Average')
  sheet1.write(0, 2, 'Freshman-Juniors Votes')
  sheet1.write(0, 3, 'Seniors Average')
  sheet1.write(0, 4, 'Seniors Votes')
  sheet1.write(0, 5, 'Alumni Average')
  sheet1.write(0, 6, 'Alumni Votes')
  sheet2.write(0, 0, 'Finalist')
  sheet2.write(0, 1, 'Commenter')
  sheet2.write(0, 2, 'Rating')
  sheet2.write(0, 3, 'Comment')

  #Keep track of the line in the second sheet.
  s2_line = 1

  for i, applicant in enumerate(applicants):
    sheet1.write(i+1, 0, '%s, %s' % (applicant.last_name, applicant.first_name))
    sheet1.write(i+1, 1, applicant.calculate_average('other'))
    sheet1.write(i+1, 2, applicant.calculate_good('other'))
    sheet1.write(i+1, 3, applicant.calculate_average('senior'))
    sheet1.write(i+1, 4, applicant.calculate_good('senior'))
    sheet1.write(i+1, 5, applicant.calculate_average('alumni'))
    sheet1.write(i+1, 6, applicant.calculate_good('alumni'))

    #Get all the feedback on an applicant ordered by descending rating
    feedbacks = Feedback.query.filter_by(applicant_id=applicant.id).\
      order_by(Feedback.rating.desc()).all()
    for feedback in feedbacks:
      commenter = User.query.filter_by(id=feedback.user_id).first()
      r = True
      f = True
      if not feedback.rating or feedback.rating == 'None':
        r = False
      if not feedback.feedback or feedback.feedback == 'None':
        f = False
      if r or f:
        sheet2.write(s2_line, 0, '%s, %s' % (applicant.last_name, applicant.first_name))
        sheet2.write(s2_line, 1, '%s' % (commenter.name))
        if r:
          sheet2.write(s2_line, 2, '%s' % (feedback.rating))
        if f: 
          sheet2.write(s2_line, 3, '%s' % (feedback.feedback))
        s2_line += 1

  with NamedTemporaryFile() as f:
    book.save(f)
    f.seek(0)
    return send_file(f.name, as_attachment=True, attachment_filename='ratings.xls')

# GET gets information from the server (server -> client)
# POST sends info to the server (client -> server)
@app.route('/', methods=['GET', 'POST'])
@app.route('/login', methods=['GET', 'POST'])
def login():
  #If the user exists and is logged in, redirect us to the homepage
  #The homepage is the index method
  if g.user is not None and g.user.is_authenticated():
    return redirect(url_for('index'))
  #Initialize the login form
  form = LoginForm()
  #If the request was a POST request (user hit Login) and the fields were valid
  if form.validate_on_submit():
    #Find the user with the email that was specified
    user = User.query.filter_by(email=form.email.data).first()
    #If the email is found in the database, check the password
    if user:
      #If the password is correct, login the user
      if check_password_hash(user.password, form.password.data):
        login_user(user, remember=True)
        #Send them to the index page, or whatever page they were trying to access
        return redirect(request.args.get('next') or url_for('index'))
      flash('Wrong Password')
    else:
      flash('No Email Found')
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
    if not form.notes.data and not form.feedback.data and form.rating.data == 'None':
      if feedback:
        db.session.delete(feedback)
        db.session.commit()
      return redirect(url_for('index'))
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

@app.route('/admin')
@login_required
def admin():
  #Get all of the users using a query.
  users = User.query.order_by(User.name).all()
  #Send users to template
  return render_template('admin.html', users=users)


@lm.user_loader
def load_user(id):
  return User.query.get(int(id))
