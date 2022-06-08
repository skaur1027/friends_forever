from flask_wtf import FlaskForm
from wtforms import StringField, SubmitField, PasswordField, BooleanField, ValidationError, SelectField, EmailField
from wtforms.validators import DataRequired, EqualTo, Length
from wtforms.validators import email_validator
from wtforms.widgets import TextArea
from flask_ckeditor import CKEditorField
from flask_wtf.file import FileField
from wtforms.fields import DateField
from wtforms import TextAreaField

# Create Forms

class UserForm(FlaskForm):
    name = StringField("Full Name", validators=[DataRequired()], render_kw={"placeholder": "John Smith"})
    email = EmailField("Email", render_kw={"placeholder": "johnsmith@gmail.com"})
    location = StringField("Location", render_kw={"placeholder": "San Francisco, CA"})
    gender = StringField("Gender", render_kw={"placeholder": "Gender"})
    birthday = DateField("Birthday", render_kw={"placeholder": "01/01/1960"})
    profession = StringField("Profession", render_kw={"placeholder": "Profession"})
    hobby = StringField("Hobby", render_kw={"placeholder": "Hobby"})
    favorite_movie = StringField("Favorite Movie", render_kw={"placeholder": "Favorite Movie"})
    favorite_book = StringField("Favorite Book", render_kw={"placeholder": "Favorite Book"})
    relationship = StringField("Relationship Status", render_kw={"placeholder": "Relationship Status"})
    password_hash = PasswordField("Password", validators=[DataRequired(),Length(min=8, max=20), EqualTo('password_hash2', message='Password must match!')], render_kw={"placeholder": "Password"})
    password_hash2 = PasswordField("Confirm Password", validators=[DataRequired()], render_kw={"placeholder": "Confirm Password"})
    profile_picture = FileField("Profile Picture")
    submit = SubmitField("Submit")

class PostForm(FlaskForm):
    title = StringField("Title", validators=[DataRequired()])
    content = CKEditorField("Content", validators=[DataRequired()])
    author = StringField("Author")
    submit = SubmitField("Submit")

class LoginForm(FlaskForm):
    email = StringField("Email", validators=[DataRequired()], render_kw={"placeholder": "Email"})
    password_hash = PasswordField('Password', validators=[DataRequired()], render_kw={"placeholder": "Password"})
    submit = SubmitField("Login")

class SearchForm(FlaskForm):
    searched = StringField("Search Friends", validators=[DataRequired()])
    submit = SubmitField("Submit")

class CommentForm(FlaskForm):
    comment = TextAreaField("Comment", validators = [DataRequired()])
    submit = SubmitField("Comment")

class ReplyForm(FlaskForm):
    reply = TextAreaField("Reply", validators = [DataRequired()])
    submit = SubmitField("Reply")

class EventsForm(FlaskForm):
    state = SelectField('State', choices=[])
    city = SelectField('City', choices=[])
    submit = SubmitField("Sumbit")
