from flask import Flask, render_template
app = Flask(__name__)

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

if __name__ == '__main__':
    app.run(debug=True)