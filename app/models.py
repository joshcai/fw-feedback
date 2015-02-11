from app import db

class Applicant(db.Model):
  id = db.Column(db.Integer, primary_key=True)
  first_name = db.Column(db.String(120), index=True)
  last_name = db.Column(db.String(120), index=True)
  feedback = db.relationship('Feedback', backref='applicant', lazy='dynamic')

  def __repr__(self):
    return '<User %r>' % (self.name)

class User(db.Model):
  id = db.Column(db.Integer, primary_key=True)
  email = db.Column(db.String(120), index=True, unique=True)
  name = db.Column(db.String(120), index=True)
  feedback = db.relationship('Feedback', backref='author', lazy='dynamic')

  def is_authenticated(self):
    return True

  def is_active(self):
    return True

  def is_anonymous(self):
    return False

  def get_id(self):
    return unicode(self.id)

  def __repr__(self):
    return '<User %r>' % (self.name)

class Feedback(db.Model):
  id = db.Column(db.Integer, primary_key = True)
  feedback = db.Column(db.String(140))
  comments = db.Column(db.String(140))
  rating = db.Column(db.Integer)
  timestamp = db.Column(db.DateTime)
  user_id = db.Column(db.Integer, db.ForeignKey('user.id'))
  applicant_id = db.Column(db.Integer, db.ForeignKey('applicant.id'))

  def __repr__(self):
    return '<Post %r>' % (self.body)