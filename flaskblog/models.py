import datetime
from flaskblog import db, loginManager, app
from flask_login import UserMixin
from itsdangerous import TimedSerializer as Serializer

@loginManager.user_loader
def user_loader(user_id):
    """find user by id and keeps session open while user is logged in"""
    return User.query.get(int(user_id))

class User(db.Model, UserMixin):
    """is a database for users, user session registration and login is managed
        in this class, UserMixin is responsible for session management, 
        see more at flask documentation
    """
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(30), unique=True, nullable=False)
    email = db.Column(db.String(150), unique=True, nullable=False)
    image_file = db.Column(db.String(20), nullable=False, default='default.jpg')
    password = db.Column(db.String(60), nullable=False)
    posts = db.relationship('Post', backref='author', lazy=True)
    
    def get_reset_token(self, expires_sec=1800):
        s = Serializer(app.config['SECRET_KEY'], expires_sec)
        return s.dumps({'user_id': self.id}).decode('utf-8')
    
    @staticmethod
    def verify_reset_token(token):
        s = Serializer(app.config['SECRET_KEY'])
        try:
            user_id = s.load(token)['user_id']
        except:
            return None
        
        return User.query.get(user_id)

    def __repr__(self):
        return "User ({}, {}, {})".format(self.username, self.email, self.image_file)

class Post(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(130), nullable=False)
    date_posted = db.Column(db.DateTime, nullable=False, default=datetime.datetime.utcnow)
    content = db.Column(db.Text, nullable=False)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    
    
    def __repr__(self):
        return "Post ({}, {})".format(self.title, self.date_posted)
