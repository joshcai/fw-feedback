from app import db
from app.models import User, Applicant, Feedback, Role, UserRoles
from werkzeug.security import generate_password_hash
import json
import random


# clear database
users = User.query.all()
applicants = Applicant.query.all()
feedback = Feedback.query.all()
roles = Role.query.all()
user_roles = UserRoles.query.all()
all_data = []
map(all_data.extend, [users, applicants, feedback, roles, user_roles])
for d in all_data:
  db.session.delete(d)
db.session.commit()

data = json.load(open('data.json'))

# add roles from data file
for role in data['roles']:
  r = Role(name=role)
  db.session.add(r)

# add applicants from data file
for applicant in data['applicants']:
  a = Applicant(first_name=applicant['first'], last_name=applicant['last'])
  db.session.add(a)

db.session.commit()

# add users from data file
for user in data['users']:
  u = User(email=user['email'],
           password=generate_password_hash(user['password']),
           name=user['name'])
  db.session.add(u)
  db.session.commit()
  for role in user['roles']:
    r = Role.query.filter_by(name=role).first()
    if r:
      ur = UserRoles(user_id=u.id, role_id=r.id)
      db.session.add(ur)
      db.session.commit()

joseph = Applicant.query.filter_by(first_name='Joseph').first()
bogdan = Applicant.query.filter_by(first_name='Bogdan').first()
hunter = Applicant.query.filter_by(first_name='Hunter').first()

apps = [joseph, bogdan, hunter]
roles = [('Freshman ', 'other'), ('Senior ', 'senior'),
         ('Alumnus ', 'alumni')]

for role in roles:
  for i in xrange(random.randint(6,9)):
    u = User(name=role[0] + str(i), email=role[0].lower().rstrip()+str(i),
             password=generate_password_hash('testpass'))
    db.session.add(u)
    db.session.commit()
    r = Role.query.filter_by(name=role[1]).first()
    if r:
      ur = UserRoles(user_id=u.id, role_id=r.id)
      db.session.add(ur)
      db.session.commit()
    for a in apps:
      if random.randint(0, 10) < 6:
        f = Feedback(user_id=u.id, applicant_id=a.id,
                     rating=random.randint(1, 5))
        db.session.add(f)
        db.session.commit()


print joseph.calculate_average('other')
print joseph.calculate_average('senior')


# print current users
users = User.query.all()
for user in users:
  print user

applicants = Applicant.query.all()
for applicant in applicants:
  print applicant