from flask import render_template, Blueprint, abort, redirect, url_for, flash, request, jsonify
from flask_login import login_required, current_user
from StudyApp.forms import *
from StudyApp.models import *
from StudyApp.utils import save_blog_picture
import os
import json

community = Blueprint("community", __name__)

file_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), '..', 'static', 'exercises.json')

@community.route("/blog/", methods=["GET"])
def blog():
    categories = Category.query.all()
    blogs = BlogPost.query.all()
    return render_template("community/blog.html", title="Blog", categories=categories, blogs=blogs)

@community.route("/blog/<string:category>/", methods=["GET"])
def blog_category(category):
    categories = Category.query.all()
    category_id = Category.query.filter_by(name=category).first_or_404().id
    blogs = BlogPost.query.filter_by(category_id=category_id).all()
    return render_template("community/blog.html", title="Blog", categories=categories, blogs=blogs)

@community.route("/blog/post/<string:blog_title>/", methods=["GET"])
def blog_post(blog_title):
    blog = BlogPost.query.filter_by(title=blog_title).first_or_404()
    paragraphs = BlogPostParagraph.query.filter_by(blog_post_id=blog.id)

    with open(file_path, 'r') as json_file:
        data = json.load(json_file)
    
    found = False
    exercises = []

    for d in data:
        if d["blog_post_id"] == blog.id:
            exercises.append(d)
            found = True
    if not found:
        exercises = False
    
    # {'blog_post_id': 1, 'alternatives': {'A': 'Alt1', 'B': 'Alt2', 'C': 'Alt3', 'D': 'Alt4'}, 'answer': 'A'}

    return render_template("community/blog_post.html", title=f"{blog.title}", blog=blog, paragraphs=paragraphs, exercises=exercises)


@community.route("/submit-quiz", methods=["POST"])
def submit_quiz():
    data = request.get_json()
    user_answers = data.get("user_answer", [])
    blog_id = data.get("blog_id")
    
    with open(file_path, 'r') as json_file:
        data = json.load(json_file)
    
    exercises = []

    for d in data:
        if d["blog_post_id"] == blog_id:
            exercises.append(d)

    if not exercises:
        return jsonify({"error": "No exercises found"}), 404

    correct = 0
    for user_ans, ex in zip(user_answers, exercises):
        if user_ans == ex["answer"]:
            print("b")
            correct += 1
    

    return jsonify({"correct": correct, "total": len(exercises)})

@login_required
@community.route("/blog/create_post/", methods=["GET", "POST"])
def create_blog():
    BlogPost.query.filter_by(id=3).delete()
    db.session.commit()
    if not current_user.is_authenticated or not current_user.is_admin:
        abort(403)
    form = NewBlogPostForm()
    categories = Category.query.all()
    if form.validate_on_submit():
        if form.picture.data:
            picture_file = save_blog_picture(form.picture.data)
        category_obj = Category.query.filter_by(name=form.category.data).first()
        category = category_obj.id
        author = current_user.username
        blog_post = BlogPost(title=form.title.data, subtitle=form.subtitle.data, author=author, image_file=picture_file, category_id=category)
        db.session.add(blog_post)
        db.session.commit()
        
        first_paragraph = BlogPostParagraph(title=form.title_paragraph.data, content=form.paragraph.data, blog_post_id=blog_post.id)
        db.session.add(first_paragraph)

        titles = request.form.getlist('title[]')
        paragraphs = request.form.getlist('paragraph[]')
        
        for t, p in zip(titles, paragraphs):
            db.session.add(BlogPostParagraph(title=t, content=p, blog_post_id=blog_post.id))

        question = request.form.getlist('question[]')
        alternativeA = request.form.getlist('alternativeA[]')
        alternativeB = request.form.getlist('alternativeB[]')
        alternativeC = request.form.getlist('alternativeC[]')
        answer = request.form.getlist('answer[]')
        
        with open(file_path, 'r') as json_file:
            exercise = json.load(json_file)

        for q, a, b, c, nswr in zip(question, alternativeA, alternativeB, alternativeC, answer):
            if not nswr.upper().strip() in ["A", "B", "C"]:
                BlogPost.query.filter_by(id=blog_post.id).delete()
                db.session.commit()
                flash({"title": "Error!", "message": f"The Answer must be A, B or C!"}, "error")
                return redirect(url_for('main.index'))
            excercise_dict = {
                "blog_post_id" : blog_post.id,
                "question" : q,
                "alternatives" : {
                    "A" : a,
                    "B" : b,
                    "C" : c
                },
                "answer" : nswr.upper().strip()
            }
            exercise.append(excercise_dict)

        with open(file_path, 'w') as json_file:
            json.dump(exercise, json_file, indent=4)

        db.session.commit()

        flash({"title": "Congratulations!", "message": f"Blog Post Created!"}, "success")
        return redirect(url_for('main.index'))
    return render_template("community/create_blog.html", title="Blog Creator", form=form, categories=categories)

@community.route("/forum/", methods=["GET", "POST"])
def forum():
    return render_template("community/forum.html", title="Forum")
