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
  a = Applicant(title=applicant['title'], first_name=applicant['first'],
    last_name=applicant['last'], group=applicant['group'],
    home_city=applicant['city'], home_state=applicant['state'],
    high_school=applicant['school'], major=applicant['major'],
    career=applicant['career'])
  db.session.add(a)

db.session.commit()

roles = ['other', 'senior', 'alumni', 'staff']

# add users from data file
for role in roles:
  for user in data[role]:
    u = User(email=user['email'],
             name=user['name'],
             activated=False)
    db.session.add(u)
    db.session.commit()
    r = Role.query.filter_by(name=role).first()
    if r:
      ur = UserRoles(user_id=u.id, role_id=r.id)
      db.session.add(ur)
      db.session.commit()

#These pointers have been mapped to actual finalists now.
# joseph = Applicant.query.all()[0]
# bogdan = Applicant.query.all()[1]
# hunter = Applicant.query.all()[5]

# apps = [joseph, bogdan, hunter]
# roles = [('Freshman ', 'other'), ('Senior ', 'senior'),
#          ('Alumnus ', 'alumni')]

# for role in roles:
#   for i in xrange(random.randint(6,9)):
#     u = User(name=role[0] + str(i), email=role[0].lower().rstrip()+str(i),
#              password=generate_password_hash('testpass'))
#     db.session.add(u)
#     db.session.commit()
#     r = Role.query.filter_by(name=role[1]).first()
#     if r:
#       ur = UserRoles(user_id=u.id, role_id=r.id)
#       db.session.add(ur)
#       db.session.commit()
#     for a in apps:
#       if random.randint(0, 10) < 6:
#         f = Feedback(user_id=u.id, applicant_id=a.id,
#                      rating=random.randint(1, 5))
#         db.session.add(f)
#         db.session.commit()

# add myself as admin:
admin = User.query.filter_by(email='jxc124730@utdallas.edu').first()
print admin
r = Role.query.filter_by(name='admin').first()
print r
ur = UserRoles(user_id=admin.id, role_id=r.id)
db.session.add(ur)
db.session.commit()

# print current users
users = User.query.all()
for user in users:
  print user

applicants = Applicant.query.all()
for applicant in applicants:
  print applicant