from flask_wtf import FlaskForm
from wtforms import StringField, SelectField, SubmitField, PasswordField
from wtforms.validators import DataRequired, Length, Email, EqualTo


class SearchForm(FlaskForm):
    q = StringField("Search by title...", validators=[DataRequired()])
    status = SelectField("Type", choices=[
        ("all", "All"),
        ("movie", "Movie"),
        ("series", "Web Series")
    ])
    submit = SubmitField("Search")


class RegisterForm(FlaskForm):
    username = StringField("Username", validators=[DataRequired(), Length(min=2, max=50)])
    email = StringField("Email", validators=[DataRequired(), Email()])
    password = PasswordField("Password", validators=[DataRequired(), Length(min=6)])
    confirm_password = PasswordField("Confirm Password", validators=[DataRequired(), EqualTo("password")])
    submit = SubmitField("Register")


class LoginForm(FlaskForm):
    username_or_email = StringField("Username or Email", validators=[DataRequired()])
    password = PasswordField("Password", validators=[DataRequired()])
    submit = SubmitField("Login")