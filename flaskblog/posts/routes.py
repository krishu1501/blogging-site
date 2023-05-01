from flask import Blueprint, render_template, url_for, flash, redirect, request, abort
from flask_login import current_user, login_required
from flaskblog import db
from flaskblog.models import Comment, Post, Reaction
from flaskblog.posts.forms import PostForm, CommentForm

posts = Blueprint('posts', __name__)



@posts.route("/post/new",methods=['GET','POST'])
@login_required
def new_post():
    form = PostForm()
    if form.validate_on_submit():
        post = Post(title=form.title.data,content=form.content.data,author=current_user)
        db.session.add(post)
        current_user.posts_count += 1
        db.session.commit()
        flash('Posted on your blog.','success')
        return redirect(url_for('main.home'))
    return render_template('create_post.html',title='Create Post', legend='New Post', form=form)

@posts.route('/post/<int:post_id>')
def post(post_id):
    post = Post.query.get_or_404(post_id)
    has_liked = has_user_liked_post(current_user.id, post_id) if current_user.is_authenticated else None
    return render_template('post.html',title=post.title, post=post, has_liked=has_liked)

@posts.route('/post/<int:post_id>/update', methods=['GET','POST'])
@login_required
def update_post(post_id):
    post = Post.query.get_or_404(post_id)
    if post.author != current_user:
        abort(403)
    form = PostForm()
    if form.validate_on_submit():
        post.title = form.title.data
        post.content = form.content.data
        db.session.commit()
        flash('Your Post has been updated.','success')
        return redirect(url_for('posts.post',post_id=post.id))
    elif request.method == 'GET':
        form.title.data = post.title
        form.content.data = post.content
    return render_template('create_post.html',title='Update Post', legend='Update Post', post=post, form=form)

@posts.route('/post/<int:post_id>/delete', methods=['POST'])
@login_required
def delete_post(post_id):
    post = Post.query.get_or_404(post_id)
    if post.author != current_user:
        abort(403)
    db.session.delete(post)
    current_user.posts_count -= 1
    db.session.commit()
    flash('Your Post has been deleted.','success')
    return redirect(url_for('main.home'))

# should the method be GET or POST
@posts.route('/post/<int:post_id>/react_on_post/<int:has_liked_int>', methods=['GET'])
@login_required
def react_on_post(post_id, has_liked_int):
    has_liked = False if has_liked_int==0 else True
    react_on_post_util(post_id, has_liked)
    flash('Your reaction on post has been saved.','success')
    return redirect(f'{request.referrer}#post-{post_id}')


@posts.route('/post/<int:post_id>/comment/new', methods=['GET','POST'])
@login_required
def new_comment(post_id):
    post = Post.query.get_or_404(post_id)
    form = CommentForm()
    if form.validate_on_submit():
        comment = Comment(content=form.content.data, post_id=post_id, user_id=current_user.get_id())
        post.comments_count += 1
        db.session.add(comment)
        flash('Successfully added your comment!','success')
        return redirect(url_for('post.post',post_id=post_id))
    return render_template('create_comment.html',title='Create Comment', legend='New Comment', form=form)


# should the method be GET or POST
@posts.route('/post/<int:post_id>/comment/<int:comment_id>/react_on_comment/<int:has_liked_int>', methods=['GET'])
@login_required
def react_on_comment(post_id, comment_id, has_liked_int):
    comment = Comment.query.get_or_404(comment_id)
    has_liked = False if has_liked_int==0 else True

    # checking if user has already reacted on this comment
    reaction = Reaction.query.filter_by(comment_id=comment_id, on_post=False, user_id=current_user.get_id()).first()
    
    if reaction is None:
        reaction = Reaction(on_post=False, has_liked=has_liked, user_id=current_user.get_id(), comment_id=comment_id)
        if has_liked:
            comment.likes_count += 1
        else:
            comment.dislikes_count += 1
        db.session.add(reaction)
    else:
        if reaction.has_liked == True and has_liked == False:
            comment.likes_count -= 1
            comment.dislikes_count += 1
            reaction.has_liked = has_liked
        elif reaction.has_liked == False and has_liked == True:
            comment.dislikes_count -= 1
            comment.likes_count += 1
            reaction.has_liked = has_liked
        elif reaction.has_liked == True and has_liked == True:
            comment.likes_count -= 1
            db.session.delete(reaction)
        elif reaction.has_liked == False and has_liked == False:
            comment.dislikes_count -= 1
            db.session.delete(reaction)
    db.session.commit()
    flash('Your reaction on comment has been saved.','success')
    return redirect(f'{request.referrer}post-#{post_id}')


@posts.route('/api/post/react_on_post', methods=['POST'])
@login_required
def react_on_post_api():
    content_type = request.headers.get('Content-Type')
    if (content_type != 'application/json'):
        abort(400)
    json = request.json
    return react_on_post_util(json.get('post_id'), json.get('has_liked'))


def react_on_post_util(post_id, has_liked):
    post = Post.query.get_or_404(post_id)
    # checking if user has already reacted on this post
    reaction = Reaction.query.filter_by(post_id=post_id, on_post=True, user_id=current_user.get_id()).first()
    
    if reaction is None:
        reaction = Reaction(on_post=True, has_liked=has_liked, user_id=current_user.get_id(), post_id=post_id)
        if has_liked:
            post.likes_count += 1
        else:
            post.dislikes_count += 1
        db.session.add(reaction)
    else:
        if reaction.has_liked == True and has_liked == False:
            post.likes_count -= 1
            post.dislikes_count += 1
            reaction.has_liked = has_liked
        elif reaction.has_liked == False and has_liked == True:
            post.dislikes_count -= 1
            post.likes_count += 1
            reaction.has_liked = has_liked
        elif reaction.has_liked == True and has_liked == True:
            post.likes_count -= 1
            db.session.delete(reaction)
        elif reaction.has_liked == False and has_liked == False:
            post.dislikes_count -= 1
            db.session.delete(reaction)
    db.session.commit()
    return {'likes':post.likes_count, 'dislikes':post.dislikes_count}

def has_user_liked_post(user_id, post_id):
    reaction = Reaction.query.filter_by(post_id=post_id, on_post=True, user_id=user_id).first()
    has_liked = reaction.has_liked if reaction else None
    return has_liked

def has_user_liked_posts(user_id, post_id_list):
    # pass only Reaction class to with_entities to get all coulumns
    reactions = Reaction.query.with_entities(Reaction.post_id, Reaction.has_liked).filter(Reaction.user_id==user_id, Reaction.post_id.in_(post_id_list), Reaction.on_post==True).all()
    has_liked_post = {}
    for reaction in reactions:
        has_liked_post.update({reaction.post_id: reaction.has_liked})
    return has_liked_post