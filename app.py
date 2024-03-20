import os

from flask import Flask, render_template, request, flash, redirect, session, g, jsonify
from sqlalchemy.exc import IntegrityError

from forms import UserAddForm, LoginForm, UserEditForm
from models import db, connect_db, User, Message, Follows
import pdb

CURR_USER_KEY = "curr_user"

app = Flask(__name__)
if __name__ == "__main__":
    app.run(debug=True)

# Get DB_URI from environ variable (useful for production/testing) or,
# if not set there, use development local db.
app.config['SQLALCHEMY_DATABASE_URI'] = (
    os.environ.get('DATABASE_URL', 'postgresql:///warbler'))
# app.config['SQLALCHEMY_DATABASE_URI'] = (os.environ.get('DATABASE_URL', "postgresql:///warbler-test"))
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['SQLALCHEMY_ECHO'] = False
app.config['DEBUG_TB_INTERCEPT_REDIRECTS'] = False
app.config['SECRET_KEY'] = os.environ.get('SECRET_KEY', "it's a secret")
app.config['SESSION_COOKIE_HTTPONLY'] = False

connect_db(app)


##############################################################################
# User signup/login/logout


@app.before_request
def add_user_to_g():
    """If we're logged in, add curr user to Flask global."""

    if CURR_USER_KEY in session:
        # updating to more current syntax
        g.user = db.session.query(User).get(session[CURR_USER_KEY])

    else:
        g.user = None

def do_login(user):
    """Log in user."""

    session[CURR_USER_KEY] = user.id

def do_logout():
    """Logout user."""
    if CURR_USER_KEY in session:
        del session[CURR_USER_KEY]

@app.route('/signup', methods=["GET", "POST"])
def signup():
    """Handle user signup.

    Create new user and add to DB. Redirect to home page.

    If form not valid, present form.

    If there already is a user with that username: flash message
    and re-present form.
    """
    if g.user:
        flash("You are already logged in.", "danger")
        return redirect("/")

    form = UserAddForm()

    if form.validate_on_submit():
        ## confirming a password is a better user experience so typos don't lead to incorrect passwords. 
        password = form.password.data
        password2 = form.password2.data
        if password != password2:
            form.password.errors=['Passwords do not match. Please try again']
            return render_template('users/signup.html', form=form)
        try:
            user = User.signup(
                username=form.username.data,
                password=form.password.data,
                email=form.email.data,
                image_url=form.image_url.data or User.image_url.default.arg,
                header_image_url = form.header_image_url.data,
                bio = form.bio.data,
                location = form.location.data
            )
            db.session.commit()

        except IntegrityError as e:
            ##differentiating between non-unique username and non-unique email
            db.session.rollback()
            if "users_email_key" in str(e):
                flash("Email already taken", "danger")
            if "users_username_key" in str(e):
                flash("Username already taken", 'danger')
            return render_template('users/signup.html', form=form)

        do_login(user)

        return redirect("/")

    else:
        return render_template('users/signup.html', form=form)


@app.route('/login', methods=["GET", "POST"])
def login():
    """Handle user login."""

    if g.user:
        flash("You are already logged in.", "danger")
        return redirect("/")

    form = LoginForm()

    if form.validate_on_submit():
        user = User.authenticate(form.username.data,
                                 form.password.data)

        if user:
            do_login(user)
            flash(f"Hello, {user.username}!", "success")
            return redirect("/")

        flash("Invalid credentials.", 'danger')

    return render_template('users/login.html', form=form)


@app.route('/logout', methods=["POST"])
def logout():
    """Handle logout of user."""

    if not g.user:
        return redirect('/login')
    else: 
        do_logout()
        flash("You have logged out.", 'success')
        return redirect('/login')


##############################################################################
# General user routes:

@app.route('/users')
def list_users():
    """Page with listing of users.

    Can take a 'q' param in querystring to search by that username.
    """
    if not g.user:
        flash("Access unauthorized.", "danger")
        return redirect("/")
    
    search = request.args.get('q')

    #updating to more current syntax
    if not search:
        users = db.session.query(User).order_by(User.username).all()
    else:
        users = db.session.query(User).filter(User.username.like(f"%{search}%")).all()

    return render_template('users/index.html', users=users)


@app.route('/users/<int:user_id>')
def users_show(user_id):
    """Show user profile."""
    
    if not g.user:
        flash("Access unauthorized.", "danger")
        return redirect("/")
    
    user = User.query.get_or_404(user_id)

    # snagging messages in order from the database;
    # user.messages won't be in order by default
    # also updating to more recent query syntax
    messages = db.session.query(Message).filter(Message.user_id == user_id).order_by(Message.timestamp.desc()).limit(100).all()

    return render_template('users/show.html', user=user, messages=messages)


@app.route('/users/<int:user_id>/following')
def show_following(user_id):
    """Show list of people this user is following."""

    if not g.user:
        flash("Access unauthorized.", "danger")
        return redirect("/")

    user = User.query.get_or_404(user_id)
    return render_template('users/following.html', user=user)


@app.route('/users/<int:user_id>/followers')
def users_followers(user_id):
    """Show list of followers of this user."""

    if not g.user:
        flash("Access unauthorized.", "danger")
        return redirect("/")

    user = User.query.get_or_404(user_id)
    return render_template('users/followers.html', user=user)

@app.route('/users/<int:user_id>/likes')
def users_likes(user_id):
    """Show list of likes of this user"""

    if not g.user:
        flash("Access unauthorized.", "danger")
        return redirect("/")

    user = User.query.get_or_404(user_id)
    return render_template('users/likes.html', user=user)


@app.route('/users/follow/<int:follow_id>', methods=['POST'])
def add_follow(follow_id):
    """Add a follow for the currently-logged-in user."""

    if not g.user:
        flash("Access unauthorized.", "danger")
        return redirect("/")

    followed_user = User.query.get_or_404(follow_id)
    g.user.following.append(followed_user)
    db.session.commit()

    return redirect(f"/users/{g.user.id}/following")


@app.route('/users/stop-following/<int:follow_id>', methods=['POST'])
def stop_following(follow_id):
    """Have currently-logged-in-user stop following this user."""

    if not g.user:
        flash("Access unauthorized.", "danger")
        return redirect("/")
    
    # updating to more current query syntax
    followed_user = db.session.query(User).get(follow_id)
    g.user.following.remove(followed_user)
    db.session.commit()

    return redirect(f"/users/{g.user.id}/following")


@app.route('/users/profile', methods=["GET", "POST"])
def profile():
    """Update profile for current user."""

    if not g.user:
        flash("Access unauthorized.", "danger")
        return redirect("/")

    # updating to more current query syntax
    form = UserEditForm(obj=g.user)
    
    if form.validate_on_submit():
        user = User.authenticate(g.user.username,
                                 form.password.data)
        if user:
            user.username = form.username.data
            user.email = form.email.data
            user.image_url = form.image_url.data
            user.header_image_url = form.header_image_url.data
            user.bio = form.bio.data
            user.location = form.location.data
            try:
                db.session.add(user)
                db.session.commit()
            except IntegrityError as e:
                db.session.rollback()
                if "users_email_key" in str(e):
                    flash("Email already taken", "danger")
                if "users_username_key" in str(e):
                    flash("Username already taken", 'danger')
                return render_template('users/edit.html', form=form, user=g.user)
            return redirect(f'/users/{user.id}')
        else: 
            flash('Invalid password. Please try again', 'danger')
            ##since only the authorized user can view this page, it's more user friendly
            ##to have them return to the form page to try their password again. 
            return render_template('users/edit.html', form=form, user=g.user)

    else:
        return render_template(f'users/edit.html', form=form, user=g.user)

@app.route('/users/add_like/<int:msg_id>', methods=["POST"])
def add_remove_likes(msg_id):
    """Adds or removes a message from a user's likes"""

    if not g.user:
        flash("Access unauthorized.", "danger")
        return redirect("/")
    
    user = db.session.query(User).get(g.user.id)
    message = db.session.query(Message).get(msg_id)

    if user.id != message.user.id:
        if message not in user.likes:
            user.likes.append(message)
            db.session.add(user)
            db.session.commit()
            return jsonify('like added')
        elif message in user.likes:
            user.likes.remove(message)
            db.session.add(user)
            db.session.commit()
            return jsonify('like removed')
    else:
        return jsonify('request failed')

@app.route('/users/delete', methods=["POST"])
def delete_user():
    """Delete user."""

    if not g.user:
        flash("Access unauthorized.", "danger")
        return redirect("/")

    do_logout()

    db.session.delete(g.user)
    db.session.commit()

    return redirect("/signup")


##############################################################################
# Messages routes:

@app.route('/messages/new', methods=["POST"])
def messages_add():
    """Add a message via ajax

    """

    if not g.user:
        flash("Access unauthorized.", "danger")
        return redirect("/")

    text = request.json['text']
    user_id = g.user.id
    new_message = Message(text=text, user_id=user_id)
    db.session.add(new_message)
    db.session.commit()

    return jsonify('message created')

@app.route('/messages/<int:message_id>', methods=["GET"])
def messages_show(message_id):
    """Show a message."""

    if not g.user:
        flash("Access unauthorized.", "danger")
        return redirect("/")

    msg = Message.query.get_or_404(message_id)
    return render_template('messages/show.html', message=msg)


@app.route('/messages/<int:message_id>/delete', methods=["POST"])
def messages_destroy(message_id):
    """Delete a message."""

    if not g.user:
        flash("Access unauthorized.", "danger")
        return redirect("/")

    # updating to more current query syntax
    msg = db.session.query(Message).get(message_id)
    if g.user.id != msg.user.id:
        flash('Access unauthorized!', "danger")
        return redirect(f'/users/{g.user.id}')
    db.session.delete(msg)
    db.session.commit()

    return redirect(f"/users/{g.user.id}")


##############################################################################
# Homepage and error pages


@app.route('/')
def homepage():
    """Show homepage:

    - anon users: no messages
    - logged in: 100 most recent messages of followed_users
    """

    if g.user:
        #updating to more recent syntax
        followed_users =[follows.user_being_followed_id for follows in db.session.query(Follows).filter(Follows.user_following_id == g.user.id).all()]
        messages = db.session.query(Message).filter((Message.user_id.in_(followed_users)) | (Message.user_id == g.user.id)).order_by(Message.timestamp.desc()).limit(100).all()

        return render_template('home.html', messages=messages)

    else:
        return render_template('home-anon.html')

@app.errorhandler(404)
def page_not_found(error):
    """Custom 404 page"""
    return render_template('404.html'), 404


##############################################################################
# Turn off all caching in Flask
#   (useful for dev; in production, this kind of stuff is typically
#   handled elsewhere)
#
# https://stackoverflow.com/questions/34066804/disabling-caching-in-flask

@app.after_request
def add_header(req):
    """Add non-caching headers on every request."""

    req.headers["Cache-Control"] = "no-cache, no-store, must-revalidate"
    req.headers["Pragma"] = "no-cache"
    req.headers["Expires"] = "0"
    req.headers['Cache-Control'] = 'public, max-age=0'
    return req


# 15 implement AJAX
# 14 fix delete messages
# 13 DRY up templates
    # testing
# 12 DRY up authorization 
    # testing
# 11 DRY up URLs
    # testing
# 10 optimize queries
    # testing
# 9 implement change password
    # testing
# 8 implement private accounts
    # testing
# 7 implement admin users
    # testing
# 6 implement user blocking
    # testing
# 5 implement direct messages
    # testing
# 4 finish implementing tests
# 3 go through the whole thing, clean up prints & console.logs, add comments, etc.
    # testing
# 2 run private tests one more time.
# 1 submit with note that the tests don't work 

