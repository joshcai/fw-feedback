from app import db

class Applicant(db.Model):

  @property
  def name(self):
    return '%s %s' % (self.first_name, self.last_name)

  @property
  def img(self):
    return '/static/img/%s,%s.jpg' % (self.last_name.title().replace('\'', ''),
                                      self.first_name.title())
  @property
  def new_img(self):
    return '/static/img/%s,%s2.jpg' % (self.last_name.title().replace('\'', ''),
                                      self.first_name.title())

  @property
  def feedback_count(self):
    return len(self.feedback.all())

  @property
  def hometown(self):
    return '%s, %s' % (self.home_city.title(), self.home_state.title())

  id = db.Column(db.Integer, primary_key=True)
  title = db.Column(db.String(120), index=True)
  first_name = db.Column(db.String(120), index=True)
  last_name = db.Column(db.String(120), index=True)
  group = db.Column(db.String(120), index=True)
  home_city = db.Column(db.String(120), index=True)
  home_state = db.Column(db.String(120), index=True)
  high_school = db.Column(db.String(120), index=True)
  major = db.Column(db.String(120), index=True)
  career = db.Column(db.String(120), index=True)
  feedback = db.relationship('Feedback', backref='applicant', lazy='dynamic')

  def calculate_average(self, role):
    f = self.feedback.join(User).join(UserRoles).join(Role).\
        filter(Role.name == role).all()
    ratings = [x.rating for x in f if isinstance(x.rating, (int, long))]
    if len(ratings) == 0:
      return None

    return sum(ratings) / float(len(ratings))

  def calculate_good(self, role):
    f = self.feedback.join(User).join(UserRoles).join(Role).\
        filter(Role.name == role).all()
    ratings = [x.rating for x in f if (isinstance(x.rating, int) and x.rating > 3)]
    return len(ratings)

  def reviewed_by(self, user):
    f = self.feedback.filter_by(user_id=user.id).all()
    return len(f) > 0

  def __repr__(self):
    return '<User %r %r>' % (self.first_name, self.last_name)

class User(db.Model):
  id = db.Column(db.Integer, primary_key=True)
  email = db.Column(db.String(120), index=True, unique=True)
  name = db.Column(db.String(120), index=True)
  password = db.Column(db.String(120))
  activated = db.Column(db.Boolean)
  feedback = db.relationship('Feedback', backref='author', lazy='dynamic')
  roles = db.relationship('UserRoles', backref='user', lazy='dynamic')

  def is_authenticated(self):
    return True

  def is_active(self):
    return True

  def is_anonymous(self):
    return False

  def get_id(self):
    return unicode(self.id)

  def has_role(self, role):
    r = Role.query.filter_by(name=role).first()
    if r:
      role_ids = [x.role_id for x in self.roles.all()]
      return r.id in role_ids
    return False

  def __repr__(self):
    return '<User %r>' % (self.name)

class Feedback(db.Model):
  id = db.Column(db.Integer, primary_key = True)
  feedback = db.Column(db.String(140))
  notes = db.Column(db.String(140))
  rating = db.Column(db.Integer)
  user_id = db.Column(db.Integer, db.ForeignKey('user.id', ondelete='CASCADE'))
  applicant_id = db.Column(db.Integer,
                           db.ForeignKey('applicant.id', ondelete='CASCADE'))


  def __repr__(self):
    return '<Feedback %r>' % (self.feedback)

class Role(db.Model):
  id = db.Column(db.Integer(), primary_key=True)
  name = db.Column(db.String(50), unique=True)
  users = db.relationship('UserRoles', backref='role', lazy='dynamic')

  def __repr__(self):
    return '<Role %r>' % (self.name)

class UserRoles(db.Model):
  id = db.Column(db.Integer(), primary_key=True)
  user_id = db.Column(db.Integer(), db.ForeignKey('user.id', ondelete='CASCADE'))
  role_id = db.Column(db.Integer(), db.ForeignKey('role.id', ondelete='CASCADE'))
