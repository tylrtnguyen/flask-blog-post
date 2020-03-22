import os
import secrets
from PIL import Image
from flask import render_template, url_for, flash, redirect, request
from flaskapp import app, db, bcrypt
from flaskapp.forms import RegistrationForm, LoginForm, UpdateAccountForm, PostForm
from flaskapp.models import User, Post
from flask_login import login_user, logout_user, login_required, current_user


@app.route('/')
@app.route('/home')
@app.route('/index')
def home():
    posts = Post.query.all()
    return render_template('home.html', posts=posts)


@app.route('/about')
def about():
    return render_template('about.html')


@app.route('/register', methods=['GET', 'POST'])
def register():
    form = RegistrationForm()
    if form.validate_on_submit():
        hashed_password = bcrypt.generate_password_hash(
            form.password.data).decode('utf-8')
        newUser = User(username=form.username.data,
                       email=form.email.data, password=hashed_password)
        db.session.add(newUser)
        db.session.commit()
        flash(f'Your account has been created! You can login now', 'success')
        return redirect(url_for('home'))
    return render_template('register.html', title='Register', form=form)


@app.route('/login', methods=['GET', 'POST'])
def login():
    form = LoginForm()
    if form.validate_on_submit():
        user = User.query.filter_by(email=form.email.data).first()
        if user and bcrypt.check_password_hash(user.password, form.password.data):
            login_user(user, remember=form.remember.data)
            next_page = request.args.get('next')
            return redirect(next_page) if next_page else redirect(url_for('home'))
        else:
            flash('Login Unsuccessful. Please check your email and password', 'danger')
    return render_template('login.html', title='Login', form=form)


@app.route('/logout')
def logout():
    logout_user()
    return redirect(url_for('login'))


# Function and route deal with user account page

def save_picture(user_picture):
    random_hex = secrets.token_hex(8)
    _, file_ext = os.path.splitext(user_picture.filename)
    picture_fname = random_hex + file_ext
    picture_path = os.path.join(
        app.root_path, 'static/profile_pics', picture_fname)
    output_size = (250, 250)
    image = Image.open(user_picture)
    image.thumbnail(output_size)
    image.save(picture_path)
    return picture_fname


@app.route('/account', methods=['GET', 'POST'])
@login_required
def account():
    form = UpdateAccountForm()
    if form.validate_on_submit():
        if form.picture.data:
            picture_file = save_picture(form.picture.data)
            current_user.image_file = picture_file
        current_user.username = form.username.data
        current_user.email = form.email.data
        db.session.commit()
        flash('Your account has been updated', 'success')
        return redirect(url_for('account'))
    elif request.method == 'GET':
        form.username.data = current_user.username
        form.email.data = current_user.email
    image_file = url_for(
        'static', filename='profile_pics/'+current_user.image_file)
    return render_template('account.html', title='Account', image_file=image_file, form=form)


# Routes deal with post
@app.route('/post/new', methods=['GET', 'POST'])
@login_required
def new_post():
    form = PostForm()
    if form.validate_on_submit():
        post = Post(title=form.title.data,
                    content=form.content.data, author=current_user)
        db.session.add(post)
        db.session.commit()
        flash('Your post has been created', 'success')
        return redirect(url_for('home'))
    return render_template('create_post.html', title='New Post', form=form)


@app.route('/post/<int:post_id>',methods=['GET', 'POST'])
def post(post_id):
    post = Post.query.get_or_404(post_id)
    post_form = PostForm()
    if post_form.validate_on_submit():
        if post_form.title.data and post_form.content.data:
            post.title = post_form.title.data
            post.content = post_form.content.data
            db.session.commit()
            flash('Your post has been updated', 'success')
            return redirect(url_for('home'))
    elif request.method == 'GET':
        post_form.title.data = post.title
        post_form.content.data = post.content
    return render_template('post.html',title='Update post',post = post,form=post_form,legend='Update post')