from flask import Flask
from datetime import datetime
from flask_sqlalchemy import SQLAlchemy
from flask_login import UserMixin
from werkzeug.security import generate_password_hash, check_password_hash
import csv

app = Flask(__name__)
db = SQLAlchemy(app)

followers = db.Table(
    'followers',
    db.Column('follower_id', db.Integer, db.ForeignKey('users.id', ondelete="CASCADE")),
    db.Column('followed_id', db.Integer, db.ForeignKey('users.id', ondelete="CASCADE"))
)


class Users(db.Model, UserMixin):
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    name = db.Column(db.String, nullable=False)
    email = db.Column(db.String, unique=True)
    location = db.Column(db.String, nullable=True)
    gender = db.Column(db.String)
    birthday = db.Column(db.DateTime)
    profession = db.Column(db.String, nullable=True)
    hobby = db.Column(db.String, nullable=True)
    favorite_movie = db.Column(db.String, nullable=True)
    favorite_book = db.Column(db.String, nullable=True)
    relationship = db.Column(db.String, nullable=True)
    password_hash = db.Column(db.String)
    profile_picture = db.Column(db.String(), nullable=True)
    date_added = db.Column(db.DateTime, default=datetime.utcnow)
    followed = db.relationship('Users',
                               secondary=followers,
                               primaryjoin=(followers.c.follower_id == id),
                               secondaryjoin=(followers.c.followed_id == id),
                               backref=db.backref('followers', lazy='dynamic'),
                               lazy='dynamic', cascade="all,delete")

    # User can have many posts
    posts = db.relationship('Post', backref='poster')
    comments = db.relationship('Comment', backref='users', passive_deletes=True)

    def follow(self, user):
        if not self.is_following(user):
            self.followed.append(user)
            return self       

    def unfollow(self, user):
        if self.is_following(user):
            self.followed.remove(user)
            return self

    def is_following(self, user):
        return self.followed.filter(
            followers.c.followed_id == user.id).count() > 0

    def followed_posts(self):
        followed = Post.query.join(
            followers, (followers.c.followed_id == Post.poster_id)).filter(
                followers.c.follower_id == self.id)
        own = Post.query.filter_by(poster_id=self.id)
        return followed.union(own).order_by(Post.date_posted.desc())

    @property
    def password(self):
        raise AttributeError('password in incorrect')

    @password.setter
    def password(self, password):
        self.password_hash = generate_password_hash(password=password)

    def verify_password(self, password):
        return check_password_hash(self.password_hash, password)

    def __repr__(self):
        return f"<User name={self.name} followed={self.followed}>"


class Post(db.Model):
    post_id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    title = db.Column(db.String)
    content = db.Column(db.Text)
    date_posted = db.Column(db.DateTime, default=datetime.utcnow)
    poster_id = db.Column(db.Integer, db.ForeignKey('users.id', ondelete='CASCADE'))
    comments = db.relationship('Comment', backref='post', passive_deletes=True)


    def __repr__(self):
        return f"<Post title={self.title} body={self.content}>"

class Comment(db.Model):
    COMMENT_LEVEL = 6

    id = db.Column(db.Integer, primary_key=True)
    text = db.Column(db.String(200), nullable=False)
    author_name = db.Column(db.String())
    date_created = db.Column(db.DateTime, default=datetime.utcnow)
    path = db.Column(db.Text, index=True)
    parent_id = db.Column(db.Integer, db.ForeignKey('comment.id'))
    author = db.Column(db.Integer, db.ForeignKey(
        'users.id', ondelete="CASCADE"), nullable=False)
    post_id = db.Column(db.Integer, db.ForeignKey(
        'post.post_id', ondelete="CASCADE"), nullable=False)

    replies = db.relationship('Comment', backref=db.backref('parent', remote_side=[id]),
        lazy='dynamic')
    
    def save(self):
        print('reached here')
        db.session.add(self)
        db.session.commit()
        prefix = self.parent.path + '.' if self.parent else ''
        self.path = prefix + '{:0{}d}'.format(self.id, self.COMMENT_LEVEL)
        db.session.commit()

    def level(self):
        return len(self.path) // self.COMMENT_LEVEL - 1
    
    def __repr__(self):
        return f"<Comment text={self.text} id={self.id}>"

class State_City(db.Model):
    __tablename__ = 'state_city'
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    state = db.Column(db.String)
    city = db.Column(db.String)

    def __repr__(self):
        return f"<State_City state={self.state} city={self.city}>"

def connect_to_db(flask_app, db_uri="postgresql:///social_app", echo=True):
    flask_app.config["SQLALCHEMY_DATABASE_URI"] = db_uri
    flask_app.config["SQLALCHEMY_ECHO"] = echo
    flask_app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False

    db.app = flask_app
    db.init_app(flask_app)

    print("Connected to the db!")

def load_data():
    with open("state_city_data.csv") as fp:
        reader = csv.reader(fp)
        data_read = [row for row in reader]

    curate_data = []
    for data in data_read:
        state = data[0]
        city = data[1]
        record = State_City(state=state, city=city)
        db.session.add(record)
        db.session.commit()

# if __name__ == "__main__":
#     from flask import Flask
#     app = Flask(__name__)
#     connect_to_db(app)
#     db.drop_all()
#     db.create_all()
#     load_data()
