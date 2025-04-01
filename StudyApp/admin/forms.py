from flask_wtf import FlaskForm
from wtforms import StringField, SubmitField, BooleanField, PasswordField, IntegerField, HiddenField
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

class UpdateCategoryForm(FlaskForm):
    id = HiddenField()
    name = StringField('Name', validators=[DataRequired(), Length(min=2, max=60)])
    submit = SubmitField('Update Category')

    def __init__(self, category=None, *args, **kwargs):
        super(UpdateCategoryForm, self).__init__(*args, **kwargs)
        self.category = category

    def validate_name(self, name):
        if self.category and name.data != self.category.name:
            existing_category = Category.query.filter_by(name=name.data).first()
            if existing_category:
                raise ValidationError("That name is taken. Please choose a different one.")

class NewCategoryForm(FlaskForm):
    name = StringField('Name',
                           validators=[DataRequired(), Length(min=2, max=60)])
    submit = SubmitField('New Category')

    def validate_name(self, name):
        category = Category.query.filter_by(name=name.data).first()
        if category:
            raise ValidationError("That Name is taken. Please choose a different one")
    