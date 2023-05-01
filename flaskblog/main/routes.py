from flask import Blueprint, request, render_template
from flaskblog.models import Post
from flaskblog.posts.routes import has_user_liked_posts
from flask_login import current_user

main = Blueprint('main', __name__)



@main.route("/")
@main.route("/home")
def home():
    page = request.args.get('page',1,type=int)
    posts = Post.query.order_by(Post.date_created.desc()).paginate(per_page=5,page=page)
    has_liked_posts = has_user_liked_posts(current_user.id, list(map(lambda post: post.id, posts.items))) if current_user.is_authenticated else {}
    return render_template('home.html', posts=posts, has_liked_posts=has_liked_posts)

@main.route("/about")
def about():
    return render_template('about.html', title='About')


