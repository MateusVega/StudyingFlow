from flask_wtf import FlaskForm
from flask_wtf.file import FileField, FileAllowed
from wtforms import StringField, SubmitField, BooleanField, PasswordField, IntegerField, HiddenField, SelectField, TextAreaField
from wtforms.validators import DataRequired, Length, Email, ValidationError
from StudyApp.models import User, BlogPost, Category, BlogPostParagraph
from flask_login import current_user

class UpdateUserForm(FlaskForm):
    id = IntegerField('Id')
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

class UpdateBlogPostForm(FlaskForm):
    id = HiddenField()
    title = StringField('Title', validators=[DataRequired(), Length(min=2, max=200)])
    subtitle = StringField('Subtitle', validators=[Length(max=300)])  # Subtitle is nullable
    category = SelectField("Choose a category", choices=[], coerce=int, validators=[DataRequired()])
    picture = FileField('Update Picture', validators=[FileAllowed(['jpg', 'png'])])
    submit = SubmitField('Update')

    def __init__(self, blog_post=None, *args, **kwargs):
        super(UpdateBlogPostForm, self).__init__(*args, **kwargs)
        self.category.choices = [(c.id, c.name) for c in Category.query.all()]

    def validate_title(self, field):
        existing_post = BlogPost.query.filter(BlogPost.title == field.data).first()
        if existing_post and existing_post.id != int(self.id.data):
            raise ValidationError("A blog post with this title already exists.")

class NewParagraphForm(FlaskForm):
    title = StringField('Title',
                           validators=[DataRequired(), Length(min=2, max=100)])
    content = TextAreaField('Content',
                           validators=[DataRequired()])
    submit = SubmitField('New Paragraph')

    def validate_title(self, title):
        paragraph = BlogPostParagraph.query.filter_by(title=title.data).first()
        if paragraph:
            raise ValidationError("That Title is taken. Please choose a different one")

class UpdateParagraphForm(FlaskForm):
    id = HiddenField()
    title = StringField('Title',
                           validators=[DataRequired(), Length(min=2, max=100)])
    content = TextAreaField('Content',
                           validators=[DataRequired()])
    submit = SubmitField('Update Paragraph')

    def validate_title(self, field):
        existing_paragraph = BlogPostParagraph.query.filter(BlogPostParagraph.title == field.data, BlogPostParagraph.id != int(self.id.data)).first()
        if existing_paragraph:
            raise ValidationError("A paragraph post with this title already exists.")