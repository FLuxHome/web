import sqlalchemy
from sqlalchemy.orm import relationship
from flask_login import UserMixin
from Shreddit import db


class User(db.Model, UserMixin):
    __tablename__ = "user"

    id = sqlalchemy.Column(sqlalchemy.Integer, primary_key=True)
    name = sqlalchemy.Column(sqlalchemy.String(20), nullable=False)
    surname = sqlalchemy.Column(sqlalchemy.String(20), nullable=False)
    birthday = sqlalchemy.Column(sqlalchemy.DateTime, nullable=False)
    email = sqlalchemy.Column(sqlalchemy.String(90), unique=True, nullable=False)
    password = sqlalchemy.Column(sqlalchemy.String(200), nullable=False)

    def __repr__(self):
        return f"User({self.name}, {self.surname}, {self.email}, {self.password})"


class Post(db.Model):
    __tablename__ = "post"

    id = sqlalchemy.Column(sqlalchemy.Integer, primary_key=True)
    posted_by = sqlalchemy.Column(sqlalchemy.Integer, sqlalchemy.ForeignKey('user.id'))
    content = sqlalchemy.Column(sqlalchemy.String(1500), nullable=False)
    date_posted = sqlalchemy.Column(sqlalchemy.DateTime, nullable=False)
    wall_posted = sqlalchemy.Column(sqlalchemy.Integer, sqlalchemy.ForeignKey("user.id"))
    user = relationship("User", backref="posts", foreign_keys=[posted_by])


class Comment(db.Model):
    __tablename__ = "comment"

    id = sqlalchemy.Column(sqlalchemy.Integer, primary_key=True)
    posted_by = sqlalchemy.Column(sqlalchemy.Integer, sqlalchemy.ForeignKey('user.id'))
    post_id = sqlalchemy.Column(sqlalchemy.Integer, sqlalchemy.ForeignKey('post.id'))
    content = sqlalchemy.Column(sqlalchemy.String(150), nullable=False)
    post = relationship("Post", backref="comments")
    user = relationship("User", backref="comments")


class Like(db.Model):
    __tablename__ = "like"

    id = sqlalchemy.Column(sqlalchemy.Integer, primary_key=True)
    liked_by = sqlalchemy.Column(sqlalchemy.Integer, sqlalchemy.ForeignKey('user.id'))
    post_id = sqlalchemy.Column(sqlalchemy.Integer, sqlalchemy.ForeignKey('post.id'), nullable=True)
    comment_id = sqlalchemy.Column(sqlalchemy.Integer, sqlalchemy.ForeignKey("comment.id"), nullable=True)
    post = relationship("Post", backref="likes")
    user = relationship("User", backref="likes")
    comment = relationship("Comment", backref="likes")


class DisLike(db.Model):
    __tablenmae__ = "dislike"

    id = sqlalchemy.Column(sqlalchemy.Integer, primary_key=True)
    disliked_by = sqlalchemy.Column(sqlalchemy.Integer, sqlalchemy.ForeignKey('user.id'))
    post_id = sqlalchemy.Column(sqlalchemy.Integer, sqlalchemy.ForeignKey('post.id'), nullable=True)
    comment_id = sqlalchemy.Column(sqlalchemy.Integer, sqlalchemy.ForeignKey("comment.id"), nullable=True)
    post = relationship("Post", backref="dislikes")
    user = relationship("User", backref="dislikes")
    comment = relationship("Comment", backref="dislikes")


class Friend(db.Model):
    __tablename__ = "friend"

    id = sqlalchemy.Column(sqlalchemy.Integer, primary_key=True)
    initiator = sqlalchemy.Column(sqlalchemy.Integer, sqlalchemy.ForeignKey("user.id"))
    recepient = sqlalchemy.Column(sqlalchemy.Integer, sqlalchemy.ForeignKey("user.id"))
    pending = sqlalchemy.Column(sqlalchemy.Boolean)
    user_i = relationship("User", backref="friends_r", foreign_keys=[recepient])
    user_r = relationship("User", backref="friends_i", foreign_keys=[initiator])


class Message(db.Model):
    __tablename__ = "message"

    id = sqlalchemy.Column(sqlalchemy.Integer, primary_key=True)
    initiator = sqlalchemy.Column(sqlalchemy.Integer, sqlalchemy.ForeignKey("user.id"))
    recepient = sqlalchemy.Column(sqlalchemy.Integer, sqlalchemy.ForeignKey("user.id"))
    date = sqlalchemy.Column(sqlalchemy.DateTime, nullable=False)
    content = sqlalchemy.Column(sqlalchemy.String(1500), nullable=False)
    user_messages_initiator = relationship("User", backref="messages", foreign_keys=[initiator])
