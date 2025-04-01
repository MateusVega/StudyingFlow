from flask_wtf import FlaskForm
from wtforms import StringField, SubmitField, BooleanField, PasswordField, IntegerField
from wtforms.validators import DataRequired, Length, Email, ValidationError
from StudyApp.models import User, BlogPost, Category
from flask_login import current_user

class UpdateUserForm(FlaskForm):
    id = IntegerField('Id') # O valor sempre será igual ao id do usuario
    username = StringField('Username',
                           validators=[DataRequired(), Length(min=2, max=20)])
    email = StringField('Email',
                           validators=[DataRequired(), Email()])
    is_admin = BooleanField('Is_admin')
    submit = SubmitField('Update User')

    def __init__(self, *args, **kwargs):
        self.user = kwargs.pop('user', None)
        super(UpdateUserForm, self).__init__(*args, **kwargs)

    def validate_username(self, username):
        if username.data != self.user.username:
            user = User.query.filter_by(username=username.data).first()
            if user:
                raise ValidationError("That username is taken. Please choose a different one")

    def validate_email(self, email):
        if email.data != self.user.email:
            user = User.query.filter_by(email=email.data).first()
            if user:
                raise ValidationError("That email is taken. Please choose a different one")

class NewUserForm(FlaskForm):
    username = StringField('Username',
                           validators=[DataRequired(), Length(min=2, max=20)])
    email = StringField('Email',
                           validators=[DataRequired(), Email()])
    password = PasswordField('Password',
                           validators=[DataRequired()])
    is_admin = BooleanField('Is_admin')
    submit = SubmitField('New User')

    def validate_username(self, username):
        user = User.query.filter_by(username=username.data).first()
        if user:
            raise ValidationError("That username is taken. Please choose a different one")
        
    def validate_email(self, email):
        user = User.query.filter_by(email=email.data).first()
        if user:
            raise ValidationError("That email is taken. Please choose a different one")