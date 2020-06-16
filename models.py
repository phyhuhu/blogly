"""Models for Blogly."""
from flask_sqlalchemy import SQLAlchemy
from datetime import datetime

db=SQLAlchemy()

def connect_db(app):
    db.app=app
    db.init_app(app)

class Users_inf(db.Model):
    __tablename__='users_inf'

    id=db.Column(db.Integer, primary_key=True, autoincrement=True)
    first_name=db.Column(db.String, nullable=False)
    last_name=db.Column(db.String, nullable=False)
    image_url =db.Column(db.String)

    posts_rel = db.relationship("Posts", backref="users_inf_rel", cascade="all, delete-orphan")

    def __repr__(self):
        return f"<Users_inf: {self.id} {self.first_name} {self.last_name} {self.image_url}>"

    @property
    def full_name(self):
        return f"{self.first_name} {self.last_name}"

class Posts(db.Model):
    __tablename__='posts'

    id=db.Column(db.Integer, primary_key=True, autoincrement=True)
    title=db.Column(db.String, nullable=False)
    content=db.Column(db.String, nullable=True)
    created_at=db.Column(db.DateTime, nullable=False, default=datetime.utcnow)
    users_inf_id=db.Column(db.Integer, db.ForeignKey('users_inf.id'), nullable=False)

    def __repr__(self):
        return f"<Posts: {self.id} {self.title} {self.created_at}>"

    @property
    def friendly_date(self):
        return self.created_at.strftime("%a %b %-d  %Y, %-I:%M %p")

class Post_Tag(db.Model):
    __tablename__='post_tag'

    post_id = db.Column(db.Integer, db.ForeignKey('posts.id'), primary_key=True)
    tag_id = db.Column(db.Integer, db.ForeignKey('tags.id'), primary_key=True)

class Tags(db.Model):
    __tablename__='tags'

    id=db.Column(db.Integer, primary_key=True, autoincrement=True)
    tag=db.Column(db.String, nullable=False)

    posts = db.relationship('Posts',secondary="post_tag", backref="tags")

    def __repr__(self):
        return f"<Tags: {self.id} {self.tag}>"