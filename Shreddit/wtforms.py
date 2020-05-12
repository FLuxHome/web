import datetime
from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, SubmitField, BooleanField, DateField, TextAreaField
from wtforms.validators import DataRequired, Length, Email, EqualTo, ValidationError
from sqlalchemy.orm.exc import NoResultFound
from Shreddit import db, login_flask
from Shreddit.orm_forms import User


@login_flask.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))


def check_unique_email(form, field):
    try:
        db.session.query(User).filter(User.email == field.data).one()
        raise ValidationError("This email is already used")
    except NoResultFound:
        return


def numbers_in_field(form, field):
    data = field.data
    for item in data:
        if item.isdigit():
            raise ValidationError("Wrong format")


class RegistrationForm(FlaskForm):
    name = StringField("Name", validators=[DataRequired(), Length(min=3, max=20), numbers_in_field])
    surname = StringField("Surname", validators=[DataRequired(), Length(min=3, max=20), numbers_in_field])
    birthday = DateField("Birthday", validators=[DataRequired()])
    email = StringField("Email", validators=[DataRequired(), Email(), check_unique_email])
    password = PasswordField("password", validators=[DataRequired()])
    confirm_password = PasswordField("Confirm Password", validators=[DataRequired(), EqualTo("password")])
    submit = SubmitField("Sign Up")


class LoginForm(FlaskForm):
    email = StringField("Username", validators=[DataRequired(), Email()])
    remember_me = BooleanField("Remember Me")
    password = PasswordField("Password", validators=[DataRequired()])
    submit = SubmitField("Login")


class PostForm(FlaskForm):
    text_field = TextAreaField("Content", validators=[DataRequired()])
    submit = SubmitField("Post")
