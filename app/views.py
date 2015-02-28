from flask import render_template, flash, redirect, session, url_for, request, g, send_file, abort
from werkzeug.security import generate_password_hash, check_password_hash
from flask_login import login_user, logout_user, current_user, login_required
from app import app, db, lm
from forms import LoginForm, FeedbackForm, FilterForm, PasswordForm, ForgotForm, AddUserForm
from models import User, Feedback, Applicant, Role, UserRoles
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
  g.ga_id = app.config['GA_ID']

@login_required
def check_viewed():
  try:
    session['viewed'] += 1
  except KeyError:
    #If the user has not seen the applicant list before, set the filter values
    #to their defaults.
    #These declarations indicate the default selections for the radio buttons
    #and checkboxes in the sorting form.
    session['viewed'] = 1
    session['sort'] = 'last'
    session['groups'] = ['1', '2', '3', '4']
    session['gender'] = ['m', 'f']
    session['location'] = ['texas', 'other']
    session['interaction'] = ['yes', 'no']


@app.route('/home', methods=['GET', 'POST'])
@login_required
def index():
  check_viewed()
  sort = session['sort']
  groups = session['groups']
  gender = session['gender']
  location = session['location']
  interaction = session['interaction']
  form = FilterForm(sort=sort, groups=groups, gender=gender, location=location,
    interaction=interaction)
  applicants = Applicant.query

  #If the form has been submitted, change the values of the fields retrieved
  #from the form to match the submission.
  if form.validate_on_submit():
    session['sort'] = form.sort.data
    session['groups'] = form.groups.data
    session['gender'] = form.gender.data
    session['location'] = form.location.data
    session['interaction'] = form.interaction.data
    return redirect(url_for('index'))

  if sort == 'first':
    applicants = applicants.order_by(Applicant.first_name)
  elif sort == 'last':
    applicants = applicants.order_by(Applicant.last_name)
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

  #Convert the query item currently pointed to by applicants into an actual list
  #of Applicants (the model type).
  applicants = applicants.all()
  if sort == 'least':
    applicants = sorted(applicants, key=lambda x: x.feedback_count)
  elif sort == 'most':
    applicants = sorted(applicants, key=lambda x: x.feedback_count, reverse=True)
  if 'yes' not in interaction:
    applicants = [applicant for applicant in applicants if not
      applicant.reviewed_by(g.user)]
  if 'no' not in interaction:
    applicants = [applicant for applicant in applicants if
      applicant.reviewed_by(g.user)]

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
def send_activation_email(user_id):
  user = User.query.get(user_id)
  token = ts.dumps(user.email, salt=app.config['SALT'])
  url = url_for('reset_password', token=token, _external=True)
  password_reset_email(user, url)
  if g.user is not None and g.user.is_authenticated() and current_user.has_role('admin'):
    flash('Email sent for user %s' % str(user_id))
  return redirect(url_for('admin'))

@app.route('/sendallresets')
@login_required
@role_required('admin')
def send_all_activation_emails():
  users = User.query.all()
  for user in users:
    token = ts.dumps(user.email, salt=app.config['SALT'])
    url = url_for('reset_password', token=token, _external=True)
    password_reset_email(user, url)
  flash('All activation emails sent')
  return redirect(url_for('admin'))

@app.route('/sendallunactivated')
@login_required
@role_required('admin')
def send_unactivated_activation_emails():
  users = User.query.filter_by(activated=False).all()
  for user in users:
    token = ts.dumps(user.email, salt=app.config['SALT'])
    url = url_for('reset_password', token=token, _external=True)
    password_reset_email(user, url)
  flash('Activation emails sent to all unactivated users')
  return redirect(url_for('admin'))

@app.route('/reset/<token>', methods=['GET', 'POST'])
def reset_password(token):
  try:
    email = ts.loads(token, salt=app.config['SALT'], max_age=86400)
  except:
    abort(404)
  user = User.query.filter_by(email=email).first()
  form = PasswordForm()
  if form.validate_on_submit():
    user.password = generate_password_hash(form.password.data)
    if not user.activated:
      user.activated = True
    db.session.add(user)
    db.session.commit()
    login_user(user, remember=True)
    return redirect(request.args.get('next') or url_for('index'))
  return render_template('password.html', title='Set Password', form=form)

@app.route('/forgot', methods=['GET', 'POST'])
def forgot_password():
  form = ForgotForm()
  if form.validate_on_submit():
    user = User.query.filter_by(email=form.email.data.lower()).first()
    if user:
      send_activation_email(user.id)
      flash('Password Reset Email Sent!')
      return redirect(url_for('login'))
    else:
      flash('Email not found')
  return render_template('forgot.html', title='Forgot Password', form=form)

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
    user = User.query.filter_by(email=form.email.data.lower()).first()
    #If the email is found in the database, check the password
    if user:
      #If the password is correct, login the user
      if not user.password:
        flash('Password not set')
      elif check_password_hash(user.password, form.password.data):
        login_user(user, remember=True)
        #Send them to the index page, or whatever page they were trying to access
        return redirect(request.args.get('next') or url_for('index'))
      else:
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

    print('Rating is %s' % form.rating.data)

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

@app.route('/admin', methods=['GET', 'POST'])
@login_required
@role_required('admin')
def admin():
  #Get all of the users using a query.
  users = User.query.order_by(User.name).all()
  form = AddUserForm()
  if form.validate_on_submit():
    u = User(email=form.email.data, name=form.name.data, activated=False)
    db.session.add(u)
    db.session.commit()
    r = Role.query.filter_by(name=form.roles.data).first()
    if r:
      ur = UserRoles(user_id=u.id, role_id=r.id)
      db.session.add(ur)
      db.session.commit()
    send_activation_email(u.id)
    flash('User added successfully, email sent')
    return redirect(url_for('admin'))
  #Send users to template
  return render_template('admin.html', users=users, form=form)


@lm.user_loader
def load_user(id):
  return User.query.get(int(id))