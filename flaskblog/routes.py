from flask import render_template, url_for, flash, redirect, request
from flask_login import login_user, logout_user, current_user, login_required
from flaskblog import app, db, bcrypt
from flaskblog.forms import RegistrationForm, LoginForm
from flaskblog.models import User, Post

posts =  [
    {
        'author': 'Krishna',
        'title': 'First post',
        'date_posted': 'April 7, 2021',
        'content': 'Could not think of any content.'
    },
    {
        'author': 'Rambo',
        'title': 'Blog post 1',
        'date_posted': 'April 7, 2021',
        'content': 'Some great content here.'
    }
]

@app.route("/")
@app.route("/home")
def home():
    return render_template('home.html', posts=posts)

@app.route("/about")
def about():
    return render_template('about.html', title='About')

@app.route("/register",methods=['GET','POST'])
def register():
    if current_user.is_authenticated:
        return redirect(url_for('home'))
    form = RegistrationForm()
    if form.validate_on_submit():
        hashed_password = bcrypt.generate_password_hash(form.password.data).decode('utf-8')
        user = User(username=form.username.data,email=form.email.data,password=hashed_password)
        db.session.add(user)
        db.session.commit()
        flash(f'Account created for {form.username.data}!','success')
        return redirect(url_for('login'))
    return render_template('register.html', title="Sign Up", form=form)

@app.route("/login",methods=['GET','POST'])
def login():
    if current_user.is_authenticated:
        return redirect(url_for('home'))
    form = LoginForm()
    if form.validate_on_submit():
        user = User.query.filter_by(email=form.email.data).first()
        if user:
            if bcrypt.check_password_hash(user.password,form.password.data):
                login_user(user, remember=form.remember.data)
                flash(f'Welcome {user.username}. You are now logged in.','success')
                next_page = request.args.get('next')
                return redirect(next_page) if next_page else redirect(url_for('home'))
            else:
                flash('Invalid Password','danger')
        else:
            flash('User is not registerd.','danger')
    return render_template('login.html', title="Login", form=form)

@app.route("/logout")
def logout():
    if current_user.is_authenticated:
        flash('Logged out','success')
    logout_user()
    return redirect(url_for('home'))

@app.route("/account")
@login_required
def account():
    return render_template('account.html')