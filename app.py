"""Blogly application."""

from flask import Flask, request, render_template, redirect, session, flash, make_response, jsonify, url_for
from flask_debugtoolbar import DebugToolbarExtension

from models import db, connect_db, Users_inf, Posts, Tags, Post_Tag

app = Flask(__name__)
app.config['SECRET_KEY'] = 'secret'
app.config['DEBUG_TB_INTERCEPT_REDIRECTS'] = False

app.config['SQLALCHEMY_DATABASE_URI'] = 'postgresql:///blogly'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['SQLALCHEMY_ECHO'] = True

connect_db(app)
db.create_all()

@app.route('/')
def root():
    posts=Posts.query.order_by(Posts.created_at.desc()).limit(5).all()
    return render_template("homepage.html", posts=posts)

@app.errorhandler(404)
def page_not_found(e):
    return render_template('404.html'), 404

@app.route("/users")
def userspage():
    names=Users_inf.query.order_by(Users_inf.last_name, Users_inf.first_name).all()
    return render_template("users/users.html", names=names)

@app.route("/users/create")
def create_user():
    names=Users_inf.query.order_by(Users_inf.last_name, Users_inf.first_name).all()
    return render_template("users/create_users.html", names=names)

@app.route("/users/create", methods=["POST"])
def add_user():
    input_list = request.form.getlist('add')

    if input_list[0]!='' or input_list[1]!='':
        user = Users_inf(first_name=input_list[0], last_name=input_list[1], image_url=input_list[2])
    else:
        return redirect("/users")

    db.session.add(user)
    db.session.commit()

    return redirect("/users")

@app.route("/users/<int:user_id>")
def show_user(user_id):
    user = Users_inf.query.get_or_404(user_id)
    posts = user.posts_rel
    return render_template("users/detail.html", user=user, posts=posts)

@app.route('/users/<int:user_id>/delete')
def delete_user(user_id):
    user = Users_inf.query.get_or_404(user_id)

    db.session.delete(user)
    db.session.commit()

    return redirect("/users")

@app.route("/users/<int:user_id>/edit")
def edit_user(user_id):
    user = Users_inf.query.get_or_404(user_id)
    return render_template("users/edit.html", user=user)

@app.route('/users/<int:user_id>/edit', methods=["POST"])
def users_update(user_id):
    input_list = request.form.getlist('edit')

    user = Users_inf.query.get_or_404(user_id)

    if input_list[0]!='':
        user.first_name = input_list[0]
    if input_list[1]!='':
        user.last_name = input_list[1]
    if input_list[2]!='':
        user.image_url = input_list[2]

    db.session.add(user)
    db.session.commit()

    return redirect(f"/users/{user.id}")

@app.route("/posts/<int:post_id>")
def show_post(post_id):
    post = Posts.query.get_or_404(post_id)
    user=post.users_inf_rel
    return render_template("posts/post_detail.html", user=user, post=post)

@app.route("/users/<int:user_id>/add")
def add_post(user_id):
    user = Users_inf.query.get_or_404(user_id)
    tags=Tags.query.all()
    return render_template("posts/add_post.html", user=user, tags=tags)

@app.route("/users/<int:user_id>/add", methods=["POST"])
def add_post_to_user(user_id):
    input_list = request.form.getlist('add_post')

    if input_list[0]!='':
        post = Posts(title=input_list[0], content=input_list[1], users_inf_id=int(user_id))
    else:
        return redirect(f'/users/{user_id}')

    db.session.add(post)
    db.session.commit()

    user = Users_inf.query.get_or_404(user_id)
    posts=user.posts_rel

    return render_template("users/detail.html", user=user, posts=posts)

@app.route('/posts/<int:post_id>/delete')
def delete_post(post_id):
    post = Posts.query.get_or_404(post_id)
    user=post.users_inf_rel

    db.session.delete(post)
    db.session.commit()

    return redirect(f"/users/{user.id}")

@app.route("/posts/<int:post_id>/edit")
def edit_post(post_id):
    post = Posts.query.get_or_404(post_id)
    user=post.users_inf_rel

    tags=Tags.query.all()

    return render_template("posts/edit_post.html", user=user, post=post, tags=tags)

@app.route('/posts/<int:post_id>/edit', methods=["POST"])
def post_update(post_id):
    input_list = request.form.getlist('edit_post')

    post = Posts.query.get_or_404(post_id)

    tag_ids = [int(num) for num in input_list[2:5] if num !='']
    post.tags = Tags.query.filter(Tags.id.in_(tag_ids)).all()

    if input_list[0]!='':
        post.title = input_list[0]
    if input_list[1]!='':
        post.content = input_list[1]

    db.session.add(post)
    db.session.commit()

    return redirect(f"/posts/{post.id}")

@app.route("/tags")
def tagspage():
    tags=Tags.query.order_by(Tags.tag).all()
    return render_template("tags/tags.html", tags=tags)

@app.route("/tags/create")
def create_tag():
    tags=Tags.query.order_by(Tags.tag).all()
    posts=Posts.query.all()
    return render_template("tags/create_tag.html", tags=tags, posts=posts)

@app.route('/tags/create', methods=["POST"])
def tag_add():
    input_list = request.form.getlist('create_tag')

    if input_list[0]!='':
        tag=Tags(tag=input_list[0])
    else:
        return redirect("/tags")

    post_ids = [int(num) for num in input_list[1:] if num !='']
    tag.posts = Posts.query.filter(Posts.id.in_(post_ids)).all()

    db.session.add(tag)
    db.session.commit()

    return redirect("/tags")

@app.route("/tags/<int:tag_id>")
def show_tag(tag_id):
    tag = Tags.query.get_or_404(tag_id)
    return render_template("tags/tag_detail.html", tag=tag)

@app.route('/tags/<int:tag_id>/delete')
def delete_tag(tag_id):
    tag = Tags.query.get_or_404(tag_id)

    db.session.delete(tag)
    db.session.commit()

    return redirect("/tags")

@app.route("/tags/<int:tag_id>/edit")
def edit_tag(tag_id):
    tag = Tags.query.get_or_404(tag_id)
    posts=Posts.query.all()

    return render_template("tags/edit_tag.html", tag=tag, posts=posts)

@app.route('/tags/<int:tag_id>/edit', methods=["POST"])
def tag_update(tag_id):
    input_list = request.form.getlist('edit_tag')

    tag = Tags.query.get_or_404(tag_id)

    if input_list[0]!='':
        tag.tag=input_list[0]

    post_ids = [int(num) for num in input_list[1:] if num !='']
    tag.posts = Posts.query.filter(Posts.id.in_(post_ids)).all()

    db.session.add(tag)
    db.session.commit()

    return redirect(f"/tags/{tag.id}")