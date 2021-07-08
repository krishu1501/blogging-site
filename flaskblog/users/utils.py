import os
import secrets
import requests
from PIL import Image
from flask import url_for, current_app
from flask_mail import Message
from flaskblog import mail
from requests_oauthlib import OAuth2Session
from flaskblog.config import Auth

def save_resized(picture,picture_path):
    output_size = (125,125)
    img = Image.open(picture)
    img.thumbnail(output_size)
    img.save(picture_path)

def save_picture(form_picture):
    random_hex = secrets.token_hex()
    _, f_ext = os.path.splitext(form_picture.filename)
    picture_fn = random_hex + f_ext
    picture_path = os.path.join(current_app.root_path, 'static/profile_pics', picture_fn)
    save_resized(form_picture,picture_path)

    return picture_fn

def save_picture_from_url(url,f_ext='png'):
    resp = requests.get(url)
    random_hex = secrets.token_hex()
    picture_fn = random_hex + '.' + f_ext
    picture_path = os.path.join(current_app.root_path, 'static/profile_pics', picture_fn)
    file = open(picture_path,'wb')
    file.write(resp.content)
    file.close()
    save_resized(picture_path,picture_path)

    return picture_fn
    
def send_reset_email(user):
    token = user.get_reset_token()
    msg = Message('Password Reset Request', sender='noreply@company.com', recipients=[user.email])
    msg.body = f'''To reset your password, visit the following link:
{url_for('users.reset_password', token=token, _external=True)}
If you did not make this request then simply ignore this email and no changes will be made.
'''
    mail.send(msg)

def get_google_auth(state=None):
    if state:
        return OAuth2Session(Auth.CLIENT_ID, state=state, redirect_uri=Auth.REDIRECT_URI)
    return OAuth2Session(Auth.CLIENT_ID, redirect_uri=Auth.REDIRECT_URI, scope=Auth.SCOPE)

def username_from_email(email, User):
    username = email[:email.index('@')]
    user = User.query.filter_by(username=username).first()
    if user is None:
        return username
    username = username + email[email.index('@')+1:email.index('.')] + email[email.index('.')+1:]
    return username