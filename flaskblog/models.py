from datetime import datetime
from flask import current_app
from flaskblog import db, login_manager
from flask_login import UserMixin
from itsdangerous import TimedJSONWebSignatureSerializer as Serializer

@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))

class User(db.Model, UserMixin):
    __tablename__ = "user"
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(25), unique=True, nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    password = db.Column(db.String(60), nullable=True)
    first_name = db.Column(db.String(50), nullable=False)
    last_name = db.Column(db.String(50), nullable=False)
    gender = db.Column(db.String(10),nullable=True)
    dob = db.Column(db.DateTime, nullable=True)
    image_file = db.Column(db.String(100), nullable=False, default='default.jpg')
    avatar_link = db.Column(db.String(200), nullable=True)
    tokens = db.Column(db.Text)
    # login_using = 'Password' for login without OAuth
    login_using = db.Column(db.String(20), nullable=False) 
    is_active = db.Column(db.Boolean, nullable=False, default=True)
    date_created = db.Column(db.DateTime, nullable=False, default=datetime.utcnow)
    last_updated = db.Column(db.DateTime, nullable=True, onupdate=datetime.utcnow)
    posts_count = db.Column(db.Integer, nullable=False, default=0)
    posts = db.relationship('Post', backref='author', lazy=True)
    comments = db.relationship('Comment', backref='author', lazy=True)
    reactions = db.relationship('Reaction', backref='author', lazy=True)

    def get_reset_token(self,expires_sec=1800):
        s = Serializer(current_app.config['SECRET_KEY'], expires_sec)
        return s.dumps({'user_id':self.id}).decode('utf-8')
    
    @staticmethod
    def verify_reset_token(token):
        s = Serializer(current_app.config['SECRET_KEY'])
        try:
            user_id = s.loads(token)['user_id']
        except:
            return None
        return User.query.get(user_id)

    def __repr__(self):
        return f"User('{self.username}','{self.email}','{self.date_created}','{self.last_updated}')"

class Post(db.Model):
    __tablename__ = "post"
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(100), nullable=False)
    content = db.Column(db.Text, nullable=False)
    date_created = db.Column(db.DateTime, nullable=False, default=datetime.utcnow)
    last_updated = db.Column(db.DateTime, nullable=True, onupdate=datetime.utcnow)
    likes_count = db.Column(db.Integer, nullable=False, default=0)
    dislikes_count = db.Column(db.Integer, nullable=False, default=0)
    comments_count = db.Column(db.Integer, nullable=False, default=0)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    comments = db.relationship('Comment', backref='orig_post', lazy=True)
    reactions = db.relationship('Reaction', backref='orig_post', lazy=True)

    def __repr__(self):
        return f"Post('{self.title}','{self.date_created}')"

class Comment(db.Model):
    __tablename__ = "comment"
    id = db.Column(db.Integer, primary_key=True)
    content = db.Column(db.Text, nullable=False)
    date_created = db.Column(db.DateTime, nullable=False, default=datetime.utcnow)
    last_updated = db.Column(db.DateTime, nullable=True, onupdate=datetime.utcnow)
    likes_count = db.Column(db.Integer, nullable=False, default=0)
    dislikes_count = db.Column(db.Integer, nullable=False, default=0)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    post_id = db.Column(db.Integer, db.ForeignKey('post.id'), nullable=False)
    reactions = db.relationship('Reaction', backref='orig_comment', lazy=True)

    def __repr__(self):
        return f"Comment('Comment {self.id}','{self.content}')"

class Reaction(db.Model):
    __tablename__ = "reaction"
    id = db.Column(db.Integer, primary_key=True)
    on_post = db.Column(db.Boolean, nullable=False, default=True)
    has_liked = db.Column(db.Boolean, nullable=False, default=True)
    date_created = db.Column(db.DateTime, nullable=False, default=datetime.utcnow)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    post_id = db.Column(db.Integer, db.ForeignKey('post.id'), nullable=True)
    comment_id = db.Column(db.Integer, db.ForeignKey('comment.id'), nullable=True)
