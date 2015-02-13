from app import db

class Applicant(db.Model):

  @property
  def name(self):
    return '%s %s' % (self.first_name, self.last_name)

  @property
  def img(self):
    return '/static/img/%s-%s.jpg' % (self.last_name.lower(), self.first_name.lower())

  id = db.Column(db.Integer, primary_key=True)
  first_name = db.Column(db.String(120), index=True)
  last_name = db.Column(db.String(120), index=True)
  feedback = db.relationship('Feedback', backref='applicant', lazy='dynamic')

  def __repr__(self):
    return '<User %r %r>' % (self.first_name, self.last_name)

class User(db.Model):
  id = db.Column(db.Integer, primary_key=True)
  email = db.Column(db.String(120), index=True, unique=True)
  name = db.Column(db.String(120), index=True)
  password = db.Column(db.String(120))
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
  applicant_id = db.Column(db.Integer, db.ForeignKey('applicant.id', ondelete='CASCADE'))

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