import os
import secrets
from PIL import Image
from flaskblog.models import User, Post
from flask import  abort, flash, redirect, render_template, request, url_for
from flaskblog import app, db, bcrypt, mail
from flaskblog.forms import (LoginForm, RegistrationForm, UpdateAccountForm, 
                                PostForm, RequestResetForm, ResetPasswordForm)
from flask_login import login_user, current_user, logout_user, login_required
from flask_mail import Message


@app.route('/')
@app.route('/home')
def home():
    page = request.args.get( 'page', 1, type=int)
    posts = Post.query.order_by(Post.date_posted.desc()).paginate(page=page, per_page=5)
    return render_template('home.html', posts=posts)

@app.route('/about')
def about():
    return render_template('about.html', title='About')

@app.route('/register', methods=['GET', 'POST'])
def register():
    """register the user into the application"""
    if current_user.is_authenticated:
        return redirect(url_for('home'))
    form = RegistrationForm()
    if form.validate_on_submit():
        hashed_pw = bcrypt.generate_password_hash(form.password.data).decode('utf-8')
        user = User(username=form.username.data,
                    email=form.email.data,
                    password=hashed_pw)
        #db.app_context().push()
        db.session.add(user)
        db.session.commit()
        flash("Account created proceed to login!!!", "success")
        return redirect(url_for('login'))
    return render_template('register.html', title='Register', form=form)

@app.route('/login', methods = ['GET', 'POST'])
def login():
    if current_user.is_authenticated:
        return redirect(url_for('home'))
    form = LoginForm()
    if form.validate_on_submit():
        user = User.query.filter_by(email=form.email.data).first()
        if user and bcrypt.check_password_hash(user.password, form.password.data):
            login_user(user, remember=form.remember_me.data)
            next_page = request.args.get('next')
            return redirect(next_page) if next_page else redirect(url_for('home')) 
        else:
            flash("Login unsucessful check email and password", "danger")

    return render_template('login.html', title='Login', form=form)

@app.route('/logout')
def logout():
    """logs the user out"""
    logout_user()
    return redirect(url_for('home'))

def save_picture(form_picture):
    """ saves picture to the picture path of the appliaction for separate users 
    the images cant be the same cos they are hashed with secrets
    it also resizes the picture before it get saved so that it will be able to save space"""
    random_hex = secrets.token_hex(8)
    _, f_ext = os.path.splitext(form_picture.filename)
    picture_fn = random_hex + f_ext
    picture_path = os.path.join(app.root_path, 'static/profile_pics', picture_fn)
    
    output_size = (125, 125)
    i = Image.open(form_picture)
    i.thumbnail(output_size)
    i.save(picture_path)
    
    return picture_fn

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
    image_file = url_for('static', filename='profile_pics/' + current_user.image_file)
    return render_template('account.html', title='Account', image_file=image_file, form=form)

@app.route('/post/new', methods=[ 'GET','POST'])
@login_required
def new_post():
    form = PostForm()
    if form.validate_on_submit():
        post = Post(title=form.title.data, content=form.content.data, author=current_user)
        db.session.add(post)
        db.session.commit()
        flash("Your post has been crated", 'success')
        return redirect(url_for('home'))
    return render_template('create_post.html', title='New Post', form=form, legend= 'Create New Post')
    
@app.route('/post/<int:post_id>')
def post(post_id):
    post = Post.query.get_or_404(post_id)
    return render_template('post.html', title=post.title, post=post)

@app.route('/post/<int:post_id>/update', methods=[ 'GET','POST'])
@login_required
def update_post(post_id):
    post = Post.query.get_or_404(post_id)
    if post.author != current_user:
        abort(403)
    form = PostForm()
    if form.validate_on_submit():
        post.title = form.title.data
        post.content = form.content.data
        db.session.commit()
        flash("Your post has been Updated", 'success')
        return redirect(url_for('post', post_id=post.id))
    elif  request.method == 'GET':
        form.title.data = post.title
        form.content.data = post.content
    return render_template('create_post.html', title='Update Post', form=form, legend= "Update Post")

@app.route('/post/<int:post_id>/delete', methods=[ 'POST' ])
@login_required
def delete_post(post_id):
    post = Post.query.get_or_404(post_id)
    if post.author != current_user:
        abort(403)
    db.session.delete(post)
    db.session.commit()
    flash("Post has been deleted!", 'sucess')
    return redirect(url_for('home'))

@login_required
@app.route('/user/<string:username>')
def user_posts(username):
    page = request.args.get( 'page', 1, type=int)
    user = User.query.filter_by(username=username).first_or_404()
    posts = Post.query.filter_by(author=user)\
            .order_by(Post.date_posted.desc())\
                .paginate(page=page, per_page=5)
    return render_template('user_posts.html', posts=posts, user=user)

def send_reset_email(user):
    token = User.get_reset_token(user)
    msg = Message('Password Reset Request', sender='noreply@demo.com', recepient=[user.email])
    msg.body = f'''
To reset your password, visit the following link: {url_for('reset_token', token=token, _external=True)}
if you did not make this request please ignore the email take no further actions.
'''

@app.route('/reset_password', methods=[ 'GET','POST'])
def reset_request():
    if current_user.is_authenticated:
        return redirect(url_for('home'))
    form = RequestResetForm()
    if form.validate_on_submit():
        user = User.query.filter_by(email=form.email.data).first()
        send_reset_email(user)
        flash('Email for password reset has been sent', 'success')
        return redirect(url_for('login'))
    return render_template('reset_request.html', title='Reset Password', form=form)

@app.route('/reset_password/<token>', methods=[ 'GET','POST'])
def reset_token(token):
    if current_user.is_authenticated:
        return redirect(url_for('home'))
    user = User.verify_reset_token(token)
    if user is None:
        flash('Invalid token or expired token', 'warning')
        return redirect(url_for('reset_request'))
    form = ResetPasswordForm()
    if form.validate_on_submit():
        hashed_pw = bcrypt.generate_password_hash(form.password.data).decode('utf-8')
        user.password = hashed_pw
        db.session.commit()
        flash("Password updated", "success")
        return redirect(url_for('login'))

    return render_template('reset_token.html', title='Reset Password', form=form)
