from flask_wtf import FlaskForm
from wtforms import StringField, SelectField, SubmitField
from wtforms.validators import DataRequired


class SearchForm(FlaskForm):
    q = StringField("Search by title...", validators=[DataRequired()])
    status = SelectField("Type", choices=[
        ("all", "All"),
        ("movie", "Movie"),
        ("series", "Web Series")
    ])
    submit = SubmitField("Search")
