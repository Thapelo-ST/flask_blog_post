import datetime
from flask import Flask, flash, redirect, render_template, request, url_for
from flask_sqlalchemy import SQLAlchemy
from forms import LoginForm, RegistrationForm

app = Flask( __name__ )
app.config['SECRET_KEY'] = '049c82008e3c97f79f7c4f'
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///site.db'
db = SQLAlchemy(app)

class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(30), unique=True, nullable=False)
    email = db.Column(db.String(150), unique=True, nullable=False)
    image_file = db.Column(db.String(20), unique=True, nullable=False, default='default.jpg')
    password = db.Column(db.String(60), nullable=False)
    posts = db.relationship('Post', backref='author', lazy=True)
    
    def __repr__(self):
        return "User ({}, {}, {})".format(self.username, self.email, self.image_file)

class Post(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(130), nullable=False)
    date_posted = db.Column(db.DateTime, nullable=False, default=datetime.datetime.utcnow)
    content = db.Column(db.Text, nullable=False)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    
    
    def __repr__(self):
        return "Post ({}, {}, {})".format(self.title, self.date_posted, self.image_file)


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
    form = RegistrationForm()
    if form.validate_on_submit():
        flash("User created successfully. For {}!!!".format(form.username.data), 'success')
        return redirect(url_for('home'))
    return render_template('register.html', title='Register', form=form)

@app.route('/login', methods = ['GET', 'POST'])
def login():
    form = LoginForm()
    if form.validate_on_submit():
        if form.email.data == 'admin01@gmail.com' and form.password.data == '12345':
            flash("You are logged in as {}".format(form.email.data), 'success')
            return redirect(url_for('home'))
        else:
            flash("login unsucessful check username and password", "danger")

    return render_template('login.html', title='Login', form=form)

if  __name__ == '__main__':
    app.run(debug=True)