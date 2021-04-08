from flask import Flask, render_template, url_for, flash, redirect
from forms import RegistrationForm, LoginForm
app = Flask(__name__)

app.config['SECRET_KEY'] = 'a33513838c99d7653d18890b97824e81'

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
    form = RegistrationForm()
    if form.validate_on_submit():
        flash(f'Account created for {form.username.data}!','success')
        return redirect(url_for('home'))
    return render_template('register.html', title="Sign Up", form=form)

@app.route("/login",methods=['GET','POST'])
def login():
    form = LoginForm()
    if form.validate_on_submit():
        if form.email.data == 'abc@123.com' and form.password.data == 'password':
            flash('You have been Logged in!','success')
            return redirect(url_for('home'))
        else:
            flash('Login Unsuccessful','danger')
    return render_template('login.html', title="Login", form=form)
    
if __name__ == '__main__':
    app.run(debug=True)