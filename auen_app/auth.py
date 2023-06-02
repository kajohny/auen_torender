from flask import Blueprint, flash, render_template, request, url_for, redirect, jsonify
from werkzeug.security import generate_password_hash, check_password_hash
from flask_login import login_required, login_user, logout_user
from .models import User
from . import db    
import re

auth = Blueprint('auth', __name__)

@auth.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == "POST":
        email = request.form.get('email')
        password = request.form.get('password')
        user = User.query.filter_by(email=email).first()
        if not user or not check_password_hash(user.password, password):
            flash('Login or password is incorrect.')
            return redirect(url_for('auth.login'))
        login_user(user)
        return redirect(url_for('main.profile'))
    return render_template('login.html')
    
@auth.route('/registration', methods=['GET', 'POST'])
def registration():
    if request.method == "POST":
        email = request.form.get('email')
        name = request.form.get('name')
        password = request.form.get('password')
        password_confirm = request.form.get('password_confirm')
        isartist = request.form.get('isartist')

        password_regex = "^(?=.*?[A-Z])(?=.*?[a-z])(?=.*?[#?!@$%^&*-]).{8,}$"

        if isartist == "artist":
            isartist = True
        else:
            isartist = False

        image = "/images/pfp/pfp_standard.jpg"
    
        user = User.query.filter_by(email=email).first()
        if user:
            flash('Email address already exists')
            return redirect(url_for('auth.login'))
        else:
            if password != password_confirm:
                flash('Passwords do not match')
            elif re.match(password_regex, password) is None:
                flash('Password should contain at least 8 characters. At least one uppercase English letter. At least one lowercase English letter. At least one special character')
            else:
                reg_user = User(email=email, name=name, password=generate_password_hash(password, method='sha256'), image=image, isartist=isartist)
                db.session.add(reg_user)
                db.session.commit()
                return redirect(url_for('auth.login'))
    return render_template('signpage.html')

@auth.route('/logout')
@login_required
def logout():
    logout_user()
    return redirect(url_for('main.index'))

