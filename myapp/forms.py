from flask_wtf import FlaskForm
from wtforms import StringField, SelectField, SubmitField, PasswordField
from wtforms.validators import DataRequired, Length, Email, EqualTo, ValidationError
from myapp.models import User
from myapp import db


def no_leading_trailing_spaces(form, field):    # (form, field) automatically passed by WTForms
    if field.data != field.data.strip():
        raise ValidationError("Field cannot have leading or trailing spaces.")

    if field.name == "password" and " " in field.data:
        raise ValidationError("Password cannot contain spaces.")


class SearchForm(FlaskForm):
    q = StringField("Search by title...", validators=[DataRequired()])
    status = SelectField("Type", choices=[
        ("all", "All"),
        ("movie", "Movie"),
        ("series", "Web Series")
    ])
    submit = SubmitField("Search")


class RegisterForm(FlaskForm):
    username = StringField("Username", validators=[DataRequired(), Length(min=2, max=50), no_leading_trailing_spaces])
    email = StringField("Email", validators=[DataRequired(), Email(), no_leading_trailing_spaces])
    password = PasswordField("Password", validators=[DataRequired(), Length(min=6), no_leading_trailing_spaces])
    confirm_password = PasswordField("Confirm Password", validators=[DataRequired(), EqualTo("password")])
    submit = SubmitField("Register")

    def validate_username(self, username):  # custom validation to check if username already exist in database                                          
        user = db.session.execute(db.select(User).where(User.username == username.data)).scalar()
        if user:
            raise ValidationError(message="This username is already taken.")


    def validate_email(self, email):  # custom validation to check if email already exist in database                                          
        user = db.session.execute(db.select(User).where(User.email == email.data)).scalar()
        if user:
            raise ValidationError(message="This email is already registered.")


class LoginForm(FlaskForm):
    username_or_email = StringField("Username or Email", validators=[DataRequired()])
    password = PasswordField("Password", validators=[DataRequired()])
    submit = SubmitField("Login")