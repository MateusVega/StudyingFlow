from flask import render_template, redirect, url_for, flash, request, jsonify
from StudyApp import app, db, bcrypt, mail
from StudyApp.models import *
from flask_login import login_user, current_user, logout_user, login_required
from flask_mail import Message
