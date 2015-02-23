from threading import Thread
from functools import wraps
from flask_login import current_user
from flask import flash, redirect, url_for

def role_required(required_role):
  def wrapper(func):
    @wraps(func)
    def decorated_view(*args, **kwargs):
      if not current_user.has_role(required_role):
          # Flash unauthorized view and redirect home
          flash('You are not authorized to view that page')
          return redirect(url_for('index'))

      # Call the actual view
      return func(*args, **kwargs)
    return decorated_view
  return wrapper

def async(f):
  def wrapper(*args, **kwargs):
    thread = Thread(target=f, args=args, kwargs=kwargs)
    thread.start()
  return wrapper
