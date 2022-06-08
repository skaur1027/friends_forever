from django.shortcuts import render
from flask import redirect, url_for, jsonify
from flask import Flask, url_for
from flask import flash
from flask import render_template
from flask import request
from forms import UserForm, PostForm, LoginForm, SearchForm, CommentForm, ReplyForm, EventsForm
from flask_sqlalchemy import SQLAlchemy
from datetime import datetime
from models import Users, Post, followers, Comment, State_City
from models import db
from flask_login import UserMixin, login_user, LoginManager, login_required, logout_user, current_user
from werkzeug.security import generate_password_hash, check_password_hash
from flask_ckeditor import CKEditor
from werkzeug.utils import secure_filename
import uuid as uuid
import os
import requests
import api_configuration as cfg
from sqlalchemy import desc, func


app = Flask(__name__)
#Add CkEditor
ckeditor = CKEditor(app)
app.config['SECRET_KEY'] = os.environ.get('flask_secret')

print(os.environ.get('flask_secret'), 'AAAAA')
print(os.environ.get('db_name'), 'DDDDD')
app.config['SQLALCHEMY_DATABASE_URI'] = os.environ.get('db_name')
app.config["SQLALCHEMY_ECHO"] = True
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False
UPLOAD_FOLDER = 'static/images'
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER

login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = 'login'

@login_manager.user_loader
def load_user(user_id):
    return Users.query.get(int(user_id))

# Pass to navbar
@app.context_processor
def base():
    form = SearchForm()
    return dict(form=form)

# Login Page
@app.route('/login', methods=['GET', 'POST'])
def login():
    form = LoginForm()
    if form.validate_on_submit():
        user = Users.query.filter_by(email=form.email.data).first()
        if user:
            if check_password_hash(user.password_hash, form.password_hash.data):
                login_user(user)
                return redirect(url_for('user', name=current_user.name))
            else:
                flash("Wrong Password - Try again")

        else:
            flash("User doesn't exist Try Again!")
    return render_template('login.html', form=form)

@app.route('/logout', methods=['GET', 'POST'])
@login_required
def logout():
    logout_user()
    return redirect(url_for('login'))


# Dashboard Page
@app.route('/dashboard', methods=['GET', 'POST'])
@login_required
def dashboard():
    form = UserForm()
    id = current_user.id
    name_to_update = Users.query.get_or_404(id)
    if request.method == "POST":
        name_to_update.name = request.form['name']
        name_to_update.email = request.form['email']
        name_to_update.location = request.form['location']
        name_to_update.gender = request.form['gender']
        name_to_update.profession = request.form['profession']
        name_to_update.hobby = request.form['hobby']
        name_to_update.favorite_movie = request.form['favorite_movie']
        name_to_update.favorite_book = request.form['favorite_book']
        name_to_update.relationship = request.form['relationship']
        

        if request.files['profile_picture']:
            name_to_update.profile_picture = request.files['profile_picture']
            picture_filename = secure_filename(name_to_update.profile_picture.filename)
            picture_name = str(uuid.uuid1()) + '_' + picture_filename
            # Save the image
            name_to_update.profile_picture.save(os.path.join(app.config['UPLOAD_FOLDER'], picture_name))

            name_to_update.profile_picture = picture_name
            # name_to_update.profile_picture = ''
            try:
                db.session.commit()
                flash("User Updated Successfully!")
                return render_template("dashboard.html",
                                    form=form,
                                    name_to_update=name_to_update)
            except Exception as error:
                flash(f"Error!  Looks like there was a problem...try again! {error}")
                return render_template("dashboard.html",
                                    form=form,
                                    name_to_update=name_to_update)
        else:
            db.session.commit()
            flash("User Updated Successfully!")
            return render_template("dashboard.html",
                                    form=form,
                                    name_to_update=name_to_update)

    else:
        return render_template("dashboard.html",
                               form=form,
                               name_to_update=name_to_update)


@app.route('/')
def index():
    return redirect(url_for('login'))

@app.route('/admin')
@login_required  
def admin():
    id = current_user.id
    users = Users.query
    posts = Post.query
    if id == 1:
        return render_template('admin.html', users=users, posts=posts)


@app.route('/user/<name>')
def user(name):
    user = Users.query.filter_by(name=name).first_or_404()
    posts = user.followed_posts()
    curr_user = Users.query.get_or_404(current_user.id)
    current_followed = curr_user.followed
    current_followed_list = []
    for record in current_followed:
        current_followed_list.append(record.id)
    return render_template('user.html', posts=posts, user=user, current_followed_list=current_followed_list)
    

@app.route('/follow/<int:id>')
def follow(id):
    user = Users.query.filter_by(id=id).first()
    if user is None:
        flash(f"User not found")
        return redirect(url_for('dashboard'))
    u = current_user.follow(user)
    if u is None:
        flash(f"Cannot follow")
        return redirect(url_for('dashboard'))
    db.session.add(u)
    db.session.commit()
    flash(f"You are now following: {user.name}")
    return redirect(url_for('user', name=user.name))

@app.route('/unfollow/<int:id>')
def unfollow(id):
    user = Users.query.filter_by(id=id).first()
    if user is None:
        flash(f"User not found")
        return redirect(url_for('dashboard'))
    u = current_user.unfollow(user)
    if u is None:
        flash(f"Cannot follow")
        return redirect(url_for('dashboard'))  
    db.session.add(u)
    db.session.commit()
    flash(f"You have stopped following: {user.name}")
    return redirect(url_for('user', name=current_user.name))


@app.route('/view_friends', methods=['GET'])
def view_friends():
    id = current_user.id
    user = Users.query.get_or_404(id)
    users = user.followed
    
    return render_template('view_friends.html', users=users)


@app.route('/friend_suggestion', methods=['GET'])
def friend_suggestion():
    id = current_user.id
    user = Users.query.get_or_404(id)
    current_friends = user.followed
    result = []
    for record in current_friends:
        result.append(record.id)
    users_location = Users.query.filter(func.lower(Users.location).like(func.lower(current_user.location)))
    users_profession = Users.query.filter(func.lower(Users.profession).like(func.lower(current_user.profession)))
    users_hobby = Users.query.filter(func.lower(Users.hobby).like(func.lower(current_user.hobby)))
    users_favorite_movie = Users.query.filter(func.lower(Users.favorite_movie).like(func.lower(current_user.favorite_movie)))
    users_favorite_book = Users.query.filter(func.lower(Users.favorite_book).like(func.lower(current_user.favorite_book)))
    users = users_location.union(users_profession).union(users_hobby).union(users_favorite_movie).union(users_favorite_book)
    # suggestions = users.filter_by(users.name!= current_friends.name)
    return render_template('friend_suggestions.html', result=result, users=users)



@app.route('/user_posts/<int:id>')
@login_required
def user_posts(id):
    posts = Post.query.order_by(desc(Post.date_posted)).all()
    return render_template('allposts.html', posts=posts)

@app.errorhandler(404)
def page_not_found(e):
    return render_template('404.html'), 404


@app.errorhandler(500)
def page_not_found(e):
    return render_template('500.html'), 500


@app.route("/allposts", methods=("GET", "POST"), strict_slashes=False)
def allposts():
    posts = Post.query.order_by(desc(Post.date_posted))
    return render_template("allposts.html", posts=posts)

@app.route('/allposts/<int:post_id>', methods=['GET', 'POST'])
@login_required
def comment(post_id):

    form = CommentForm()
    form2 = ReplyForm()

    post = Post.query.get_or_404(post_id)
    comments = Comment.query.filter_by(post_id=post.post_id).order_by(Comment.path.asc())
    if request.method == 'POST':

        if form.validate_on_submit():
            author_name = current_user.name
            text = form.comment.data
            author_id = current_user.id
            comment = Comment(text=text, author_name=author_name, author=author_id, post_id=post.post_id)
            comment.save()

            form.comment.data = ''

    return render_template('comments.html', post=post, form1=form,
        form2=form2, comments=comments)


@app.route("/allposts/<int:post_id>/<int:comment_id>",methods=("GET", "POST"),strict_slashes=False)
@login_required
def reply_comment(post_id,comment_id):
    form1 = CommentForm()
    form = ReplyForm()
    post = Post.query.first_or_404(post_id)
    parent = Comment.query.filter_by(id=comment_id).first_or_404()
    comments = Comment.query.filter_by(post_id=post.post_id).order_by(Comment.path.asc())

    if request.method == 'POST':
        if form.validate_on_submit():
            author_name = current_user.name
            text = form.reply.data
            author_id = current_user.id
            comment = Comment(parent=parent, text=text, author_name=author_name, author=author_id, post_id=post.post_id)
            comment.save()
            form.reply.data = ''
            return redirect(url_for('comment', post_id=post.post_id))

    return render_template('comments.html', post=post, form2=ReplyForm(), form1=CommentForm(), comments=comments, parent=parent)


@app.route('/user/add', methods=['GET', 'POST'])
def add_user():
    name = None
    email = None
    form = UserForm()
    if form.validate_on_submit():
        user = Users.query.filter_by(email=form.email.data).first()
        if user is None:
            hashed_password = generate_password_hash(form.password_hash.data, 'sha256')
            user = Users(name=form.name.data, email=form.email.data, birthday=form.birthday.data, password_hash=hashed_password)
            db.session.add(user)
            db.session.commit()
            flash("Account created. Please login.")
            return redirect(url_for('login'))
        else:
            flash("Account already exists. Please try again")
            return redirect(url_for('add_user'))

    name = form.name.data
    email = form.email.data
    form.name.data = ''
    form.email.data = ''
    form.birthday.data = ''
    form.password_hash.data = ''
    our_users = Users.query.order_by(Users.date_added)
    return render_template('add_users.html', form=form, name=name, our_users=our_users)


# Update DB record and make changes in the dashboard page
@app.route('/update/<int:id>', methods=['GET', 'POST'])
@login_required
def update_user(id):
    form = UserForm()
    name_to_update = Users.query.get_or_404(id)
    if request.method == "POST":
        name_to_update.name = request.form['name']
        name_to_update.email = request.form['email']
        name_to_update.gender = request.form['gender']
        name_to_update.location = request.form['location']
        name_to_update.profession = request.form['profession']
        name_to_update.hobby = request.form['hobby']
        name_to_update.favorite_movie = request.form['favorite_movie']
        name_to_update.favorite_book = request.form['favorite_book']
        name_to_update.relationship = request.form['relationship']

        if request.files["profile_picture"]:
            # Check for profile pic
            name_to_update.profile_picture = request.files["profile_picture"]
            # Image name
            pic_filename = secure_filename(name_to_update.profile_picture.filename)
            # Set UUID
            pic_name = str(uuid.uuid1()) + "_" + pic_filename
            # Save image
            saver = request.files["profile_picture"]
            # Change image to string to save to database
            name_to_update.profile_picture = pic_name
            try:
                saver.save(os.path.join(app.config["UPLOAD_FOLDER"], pic_name))
                db.session.commit()
                flash("User updated successfully.")
                return render_template("user.html", form=form, name_to_update=name_to_update)
            except:
                flash("Try again.")
                return render_template("update_user.html", form=form, name_to_update=name_to_update)
        else:
            db.session.commit()
            flash("User updated successfully.")
            return render_template("update_user.html", form=form, name_to_update=name_to_update)
    else:
        return render_template("update_user.html", form=form, name_to_update=name_to_update, id=id)

# Delete a record
@app.route('/delete/<int:id>')
@login_required
def delete_record(id):
    name = None
    form = UserForm()
    user_to_delete = Users.query.filter_by(id=id).delete()
    if current_user.id == 1:
        db.session.commit()
        our_users = Users.query.order_by(Users.date_added)
        return redirect(url_for('admin'))
    else:
        logout_user()
        db.session.commit()
        flash(f"Your account has been deleted!")
        our_users = Users.query.order_by(Users.date_added)
        return render_template('add_users.html', form=form, name=name, our_users=our_users)

@app.route('/add-post', methods=['GET', 'POST'])
# @login_required
def add_post():
    form = PostForm()
    if form.validate_on_submit():
        poster = current_user.id
        post = Post(title=form.title.data, content=form.content.data, poster_id=poster)
        form.content.data = ''
        form.title.data = ''

        db.session.add(post)
        db.session.commit()
        return redirect(url_for('allposts'))
    
    return render_template("add_post.html", form=form)

@app.route('/allposts/<int:id>')
def post(id):
    post = Post.query.get_or_404(id)
    return render_template('post.html', post=post)

@app.route('/allposts/edit/<int:id>', methods=['GET', 'POST'])
@login_required
def edit_post(id):
    post = Post.query.get_or_404(id)
    form = PostForm()
    if form.validate_on_submit():
        post.title = form.title.data
        post.content = form.content.data

        db.session.add(post)
        db.session.commit()

        return redirect(url_for('allposts', id=post.post_id))

    if current_user.id == post.poster.id:
        form.title.data = post.title
        form.content.data = post.content

        return render_template('edit_post.html', form=form) 
    else:
        flash(f"Not authorized to edit this Post")
        posts = Post.query.order_by(Post.date_posted)

        return render_template('allposts.html', posts=posts)        


@app.route("/posts/delete/<int:id>")
@login_required
def delete_post(id):
    post_to_delete = Post.query.get_or_404(id)
    id = current_user.id
    if id == post_to_delete.poster.id:

        try:
            db.session.delete(post_to_delete)
            db.session.commit()

            # Grab all the posts from the database
            posts = Post.query.order_by(Post.date_posted)
            return render_template("allposts.html", posts=posts)

        except:
            # Return error message
            flash("There was an error deleting the post. Try again.")

            # Grab all the posts from the database
            posts = Post.query.order_by(Post.date_posted)
            return render_template("allposts.html", posts=posts)
        
    elif id == 1:
        try:
            db.session.delete(post_to_delete)
            db.session.commit()

            # Grab all the posts from the database
            posts = Post.query.order_by(Post.date_posted)
            return render_template("admin.html", posts=posts)

        except:
            # Return error message
            flash("There was an error deleting the post. Try again.")

    else:
        flash("You are not authorized to delete this post.")

        # Grab all the posts from the database
        posts = Post.query.order_by(Post.date_posted)
        return render_template("allposts.html", posts=posts)


# Ceate a search function
@app.route('/search', methods=['GET','POST'])
def search():
    curr_user = Users.query.get_or_404(current_user.id)
    current_followed = curr_user.followed
    current_followed_list = []
    for record in current_followed:
        current_followed_list.append(record.id)
    form = SearchForm()
    users = Users.query
    posts = Post.query
    if form.validate_on_submit():
        searched = request.form["searched"]
        tag = request.form["searched"]
        search = "%{}%".format(tag)
        users = Users.query.filter(func.lower(Users.name).like(func.lower(search)))
        locations = Users.query.filter(Users.location.like(search))
        profession = Users.query.filter(func.lower(Users.profession).like(func.lower(search)))
        users = users.union(locations).union(profession)

        posts = Post.query.filter(func.lower(Post.title).like(func.lower(search)))
        content = Post.query.filter(func.lower(Post.content).like(func.lower(search)))
        posts = posts.union(content)

        form.searched.data = ''
        return render_template('search.html', form=form, searched=searched,
                                users=users, posts=posts, locations=locations, current_followed_list=current_followed_list)


@app.route('/events', methods=['GET', 'POST'])
def state_city():
    states = db.session.query(State_City.state).group_by('state').order_by('state').all()
    states_data = []

    for data in states:
        states_data.append(list(data._asdict().values())[0])
    state_city_data = State_City.query.order_by('city')
    form = EventsForm()
    form.state.choices = states_data
    form.city.choices = [data.city for data in state_city_data]

    if request.method == 'POST':
        city = State_City.query.filter_by(id=form.city.data).first()
        return redirect(url_for('show_events', state=form.state.data, city=city.city))
    form.city.data = ''
    form.state.data = ''
    return render_template('events.html', form=form)

@app.route('/city/<state>')
def city(state):
    cities = State_City.query.filter_by(state=state).all()
    cityArray = []
    for city in cities:
        cityObj = {}
        cityObj['id'] = city.id
        cityObj['name'] = city.city
        cityArray.append(cityObj)

    return jsonify({'cities' : cityArray})

@app.route('/api_events/<state>/<city>', methods=['GET', 'POST'])
def api_events(state, city):
    return render_template('events', state=state, city=city)

@app.route('/show_events/<state>/<city>', methods=['GET', 'POST'])
def show_events(state, city):
    base_url = cfg.base_url
    params = cfg.params
    params['city'] = city
    params['stateCode'] = state
    response = requests.get(base_url, params=params)
    if response.status_code == 200:
        data = response.json().get('_embedded').get('events')
        return render_template('all_events.html', data=data)
    else:
        flash(f"No events found in {city},{state}.")

if __name__ == "__main__":
    db.init_app(app)
    app.run(debug=True)
