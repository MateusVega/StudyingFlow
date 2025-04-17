from flask_wtf import FlaskForm
from flask_wtf.file import FileField, FileAllowed
from wtforms import StringField, PasswordField, SubmitField, BooleanField, SelectField, TextAreaField
from wtforms.validators import DataRequired, Length, Email, EqualTo, ValidationError
from StudyApp.models import User, BlogPost, Category
from flask_login import current_user

class RegistrationForm(FlaskForm):
    username = StringField('Username',
                           validators=[DataRequired(), Length(min=2, max=20)])
    email = StringField('Email',
                           validators=[DataRequired(), Email()])
    password = PasswordField('Password',
                           validators=[DataRequired()])
    confirm_password = PasswordField('Confirm Password',
                           validators=[DataRequired(), EqualTo('password')])
    
    submit = SubmitField('Sign Up')

    def validate_username(self, username):
        user = User.query.filter_by(username=username.data).first_or_404()
        if user:
            raise ValidationError("That username is taken. Please choose a different one")
        
    def validate_email(self, email):
        user = User.query.filter_by(email=email.data).first_or_404()
        if user:
            raise ValidationError("That email is taken. Please choose a different one")

class LoginForm(FlaskForm):
    email = StringField('Email',
                           validators=[DataRequired(), Email()])
    password = PasswordField('Password',
                           validators=[DataRequired()])
    remember = BooleanField('Remember Me')
    
    submit = SubmitField('Login')

class UpdateAccountForm(FlaskForm):
    picture = FileField('Update Profile Picture',
                            validators=[FileAllowed(['jpg', 'png', 'jpeg'])])
    username = StringField('Username',
                           validators=[DataRequired(), Length(min=2, max=20)])
    email = StringField('Email',
                           validators=[DataRequired(), Email()])
    current_password = PasswordField('Current Password')
    new_password = PasswordField('New Password')
    submit = SubmitField('Update')

    def validate_username(self, username):
        user = User.query.filter_by(username=username.data).first_or_404()
        if user and user != current_user:
            raise ValidationError("That username is taken. Please choose a different one")
        
    def validate_email(self, email):
        user = User.query.filter_by(email=email.data).first_or_404()
        if user and user != current_user:
            raise ValidationError("That email is taken. Please choose a different one")

class ResetRequestForm(FlaskForm):
    email = StringField('Email',
                           validators=[DataRequired(), Email()])
    submit = SubmitField('Reset Password')

class ResetPasswordForm(FlaskForm):
    password = PasswordField('Password',
                           validators=[DataRequired()])
    confirm_password = PasswordField('Confirm Password',
                           validators=[DataRequired(), EqualTo('password')])
    submit = SubmitField('Update Password')

class NewBlogPostForm(FlaskForm):
    title = StringField('Title',
                           validators=[DataRequired(), Length(min=2, max=200)])
    subtitle = StringField('Subtitle',
                           validators=[DataRequired(), Length(min=2, max=300)])
    category = SelectField("Choose a category", choices=[])
    picture = FileField('Update Profile Picture', validators=[DataRequired(), FileAllowed(['jpg', 'png'])])
    title_paragraph = StringField('Title of Paragraph')
    paragraph = TextAreaField('Paragraph')
    
    submit = SubmitField('Create')

    def validate_title(self, title):
        post = BlogPost.query.filter_by(title=title.data).first()
        if post:
            raise ValidationError("That title is taken. Please choose a different one")
    
    def __init__(self, *args, **kwargs):
        super(NewBlogPostForm, self).__init__(*args, **kwargs)
        self.category.choices = [(c.name, c.name) for c in Category.query.all()]
        