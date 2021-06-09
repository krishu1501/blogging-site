from flask import Blueprint, render_template, url_for, flash, redirect, request
from flask_login import login_user, logout_user, current_user, login_required
from flaskblog import db, bcrypt
from flaskblog.users.forms import RegistrationForm, LoginForm, UpdateAccountForm, ResetRequestForm, ResetPasswordForm, ChangePasswordForm
from flaskblog.models import User, Post
from flaskblog.users.utils import save_picture, send_reset_email


users = Blueprint('users', __name__)

@users.route("/register",methods=['GET','POST'])
def register():
    if current_user.is_authenticated:
        return redirect(url_for('main.home'))
    form = RegistrationForm()
    if form.validate_on_submit():
        hashed_password = bcrypt.generate_password_hash(form.password.data).decode('utf-8')
        user = User(username=form.username.data,email=form.email.data,password=hashed_password)
        db.session.add(user)
        db.session.commit()
        flash(f'Account created for {form.username.data}!','success')
        return redirect(url_for('users.login'))
    return render_template('register.html', title="Sign Up", form=form)

@users.route("/login",methods=['GET','POST'])
def login():
    if current_user.is_authenticated:
        return redirect(url_for('main.home'))
    form = LoginForm()
    if form.validate_on_submit():
        user = User.query.filter_by(email=form.email.data).first()
        if user:
            if bcrypt.check_password_hash(user.password,form.password.data):
                login_user(user, remember=form.remember.data)
                flash(f'Welcome {user.username}. You are now logged in.','success')
                next_page = request.args.get('next')
                return redirect(next_page) if next_page else redirect(url_for('main.home'))
            else:
                flash('Invalid Password','danger')
        else:
            flash('User is not registerd.','danger')
    return render_template('login.html', title="Login", form=form)

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
        current_user.username = form.username.data
        current_user.email = form.email.data
        db.session.commit()
        flash('Your details were updated!','success')
        return redirect(url_for('users.account'))
    elif password_form.validate_on_submit() and formid==2:
        if bcrypt.check_password_hash(current_user.password, password_form.current_password.data):
            hashed_password = bcrypt.generate_password_hash(password_form.new_password.data).decode('utf-8')
            current_user.password = hashed_password
            db.session.commit()
            flash('Password updated successfully!','success')
        else:
            flash('Current password entered is incorrect!','danger')
        return redirect(url_for('users.account'))
    if request.method == 'GET':
        form.username.data = current_user.username
        form.email.data = current_user.email
    image_file = url_for('static',filename='profile_pics/'+current_user.image_file)
    return render_template('account.html', title='Account', image_file=image_file, form=form, password_form=password_form)

@users.route("/user/<string:username>")
def user_posts(username):
    page = request.args.get('page',1,type=int)
    user = User.query.filter_by(username=username).first_or_404()
    posts = Post.query.filter_by(author=user)\
        .order_by(Post.date_posted.desc())\
        .paginate(per_page=5,page=page)
    return render_template('user_posts.html', posts=posts, user=user)

@users.route("/reset_password", methods=['GET','POST'])
def request_reset_password():
    if current_user.is_authenticated:
        return redirect(url_for('main.home'))
    form = ResetRequestForm()
    if form.validate_on_submit():
        user = User.query.filter_by(email=form.email.data).first()
        send_reset_email(user)
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