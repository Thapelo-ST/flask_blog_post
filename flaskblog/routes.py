import os
import secrets
from PIL import Image
from flaskblog.models import User, Post
from flask import  flash, redirect, render_template, request, url_for
from flaskblog import app, db, bcrypt
from flaskblog.forms import LoginForm, RegistrationForm, UpdateAccountForm
from flask_login import login_user, current_user, logout_user, login_required

posts = [
    {
        'author' : ' Amen to god',
        'title' : ' Book of enoch',
        'content' : ' first content',
        'date' : ' 1800 BC'
    },
    {
        'author' : 'Gabriel',
        'title' : ' Bible',
        'content' : ' second content',
        'date' : '1540 AC '
    }
]


@app.route('/')
@app.route('/home')
def home():
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
