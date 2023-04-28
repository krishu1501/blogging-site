import json
from flask import Blueprint, render_template, url_for, flash, redirect, request, session
from flask_login import login_user, logout_user, current_user, login_required
from flaskblog import db, bcrypt
from flaskblog.users.forms import RegistrationForm, LoginForm, UpdateAccountForm, ResetRequestForm, ResetPasswordForm, ChangePasswordForm
from flaskblog.models import User, Post
from flaskblog.users.utils import get_google_auth, save_picture, send_reset_email, username_from_email, save_picture_from_url
from flaskblog.config import Auth
from flaskblog.reference import profile_pics_predef


users = Blueprint('users', __name__)

@users.route("/register",methods=['GET','POST'])
def register():
    if current_user.is_authenticated:
        return redirect(url_for('main.home'))
    form = RegistrationForm()
    if form.validate_on_submit():
        hashed_password = bcrypt.generate_password_hash(form.password.data).decode('utf-8')
        user = User(first_name=form.first_name.data,last_name=form.last_name.data,username=form.username.data,email=form.email.data,password=hashed_password,login_using='Password')
        db.session.add(user)
        db.session.commit()
        login_user(user)
        flash(f'Welcome, {user.username}.','success')
        next_page = request.args.get('next')
        return redirect(next_page) if next_page else redirect(url_for('main.home'))
    return render_template('register.html', title="Sign Up", form=form)

@users.route("/login/<prompt>")
@users.route("/login",methods=['GET','POST'])
def login(prompt=None):
    if current_user.is_authenticated:
        return redirect(url_for('main.home'))
    form = LoginForm()
    if form.validate_on_submit():
        user = User.query.filter_by(email=form.email.data).first()
        if user is None:
            flash('Invalid Password','danger')
        elif user.login_using!='Password':
            flash(f'You have used {user.login_using} to login before. Please use the same to login!','danger')
        else:
            if bcrypt.check_password_hash(user.password,form.password.data):
                login_user(user, remember=form.remember.data)
                flash(f'Welcome {user.username}. You are now logged in.','success')
                next_page = request.args.get('next')
                return redirect(next_page) if next_page else redirect(url_for('main.home'))
            else:
                flash('Invalid Password','danger')
    oauth = get_google_auth()
    auth_url, state = oauth.authorization_url(Auth.AUTH_URI, access_type='offline', prompt=prompt)
    session['oauth_state'] = state
    return render_template('login.html', title="Login", form=form, auth_url=auth_url)

@users.route("/oauth2callback")
def callback():
    if current_user is not None and current_user.is_authenticated:
        return redirect(url_for('main.home'))
    if 'error' in request.args:
        if request.args.get('error') == 'access_denied':
            flash('You denied access.','danger')
        else:
            flash('Error occured','danger')
        return redirect(url_for('users.login'))
    if 'code' not in request.args or 'state' not in request.args:
        flash('Error Occurred! Please try again.')
        return redirect(url_for('users.login'))
    else:
        print()
        print('code: ', request.args.get('code'))
        print('request.url: ',request.url)
        print()

    oauth = get_google_auth(state=session['oauth_state'])
    try:
        token = oauth.fetch_token(Auth.TOKEN_URI, client_secret=Auth.CLIENT_SECRET, authorization_response=request.url)
    except Exception as e:
        print("Error: ", e)
        flash('Error Occurred while getting access token','danger')
        return redirect(url_for('users.login'))
    resp = oauth.get(Auth.USER_INFO)
    if resp.status_code == 200:
        user_data = resp.json()
        email = user_data['email']
        # print()
        # print(user_data)
        # print('Name: ',user_data['name'])
        # print('Email: ',user_data['email'])
        # print('Picture link: ',user_data['picture'])
        # print()
        
        user = User.query.filter_by(email=email).first()
        if user is not None:
            if user.login_using!='Google':
                flash(f'You have not used Google to login before. Please use email and password to login!','danger')
                return redirect(url_for('users.login'))
            flash(f'Welcome back, {user.username}.','success')
            user.login_using = 'Google'
        else:
            user = User()
            user.username = username_from_email(email,User)
            user.first_name = user_data['given_name']
            user.last_name = user_data['family_name']
            user.email = email
            user.avatar_link = user_data['picture']
            user.image_file = save_picture_from_url(user_data['picture'])
            user.tokens = json.dumps(token)
            user.login_using = 'Google'
            flash(f'Welcome, {user.username}.','success')
        db.session.add(user)
        db.session.commit()
        login_user(user)
        return redirect(url_for('main.home'))       
    else:
        flash('Could not fetch your information','danger')
        return redirect(url_for('users.login'))

@users.route("/logout")
def logout():
    if current_user.is_authenticated:
        flash('Logged out','success')
        logout_user()
    return redirect(url_for('main.home'))

@users.route("/account",methods=['GET','POST'])
@login_required
def account():
    form = UpdateAccountForm()
    password_form = ChangePasswordForm()
    formid = request.args.get('formid',1,type=int)
    if form.validate_on_submit() and formid==1:
        if form.picture.data:
            picture_fn = save_picture(form.picture.data)
            current_user.image_file = picture_fn
        elif form.predef_picture.data in profile_pics_predef:
            current_user.image_file = form.predef_picture.data
        current_user.first_name = form.first_name.data
        current_user.last_name = form.last_name.data
        current_user.username = form.username.data
        current_user.email = form.email.data
        current_user.dob = form.dob.data
        current_user.gender = form.gender.data
        db.session.commit()
        flash('Your details were updated!','success')
        return redirect(url_for('users.account'))
    elif password_form.validate_on_submit() and formid==2:
        if current_user.login_using!='Password':
            flash(f'You have used {current_user.login_using} to login. Password was not used.','info')
        elif bcrypt.check_password_hash(current_user.password, password_form.current_password.data):
            hashed_password = bcrypt.generate_password_hash(password_form.new_password.data).decode('utf-8')
            current_user.password = hashed_password
            db.session.commit()
            flash('Password updated successfully!','success')
        else:
            flash('Current password entered is incorrect!','danger')
        return redirect(url_for('users.account'))
    if request.method == 'GET':
        form.username.data = current_user.username
        form.first_name.data = current_user.first_name
        form.last_name.data = current_user.last_name
        form.email.data = current_user.email
        form.dob.data = current_user.dob
        form.gender.data = current_user.gender
    image_file = url_for('static',filename='profile_pics/'+current_user.image_file)
    profile_pics_paths = {}
    for name in profile_pics_predef:
        profile_pics_paths[name] = url_for('static', filename='profile_pics/'+name)
    return render_template('account.html', title='Account', image_file=image_file, profile_pics_paths=profile_pics_paths, form=form, password_form=password_form)

@users.route("/user/<string:username>")
def user_posts(username):
    page = request.args.get('page',1,type=int)
    user = User.query.filter_by(username=username).first_or_404()
    posts = Post.query.filter_by(author=user)\
        .order_by(Post.date_created.desc())\
        .paginate(per_page=5,page=page)
    return render_template('user_posts.html', posts=posts, user=user)

@users.route("/reset_password", methods=['GET','POST'])
def request_reset_password():
    if current_user.is_authenticated:
        return redirect(url_for('main.home'))
    form = ResetRequestForm()
    if form.validate_on_submit():
        user = User.query.filter_by(email=form.email.data).first()
        try:
            send_reset_email(user)
        except:
            flash('This serice is currently unavailable','danger')
            return redirect(url_for('users.request_reset_password'))
        flash('Instruction to reset password has been sent to your email.','info')
        return redirect(url_for('users.login'))
    return render_template('reset_request.html', title='Reset Password', form=form)

@users.route("/reset_password/<string:token>", methods=['GET','POST'])
def reset_password(token):
    if current_user.is_authenticated:
        return redirect(url_for('main.home'))
    user = User.verify_reset_token(token)
    if user is None:
        flash('Invalid/Expired token.','warning')
        return redirect(url_for('users.request_reset_password'))
    form = ResetPasswordForm()
    if form.validate_on_submit():
        hashed_password = bcrypt.generate_password_hash(form.password.data).decode('utf-8')
        user.password = hashed_password
        db.session.commit()
        flash('Password updated successfully!','success')
        return redirect(url_for('users.login'))
    return render_template('reset_password.html', title='Reset Password', form=form)