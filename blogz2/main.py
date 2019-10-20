from flask import Flask, request, redirect, render_template, session, flash
from flask_sqlalchemy import SQLAlchemy
import os

app = Flask(__name__)
app.config['DEBUG'] = True
app.config['SQLALCHEMY_DATABASE_URI'] = 'mysql+pymysql://Blogz3:Blogz3@localhost:8889/Blogz3'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db = SQLAlchemy(app)
app.secret_key = "y337kGcys&zP3B"


class Post(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(120))
    body = db.Column(db.Text)
    
    owner_id = db.Column(db.Integer, db.ForeignKey("user.id"))

    def __init__(self, title, body, owner):
        self.title = title
        self.body = body
        self.owner = owner


class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(120), unique=True)
    password = db.Column(db.String(120))
    posts = db.relationship("Post", backref="owner")

    def __init__(self, username, password):
        self.username = username
        self.password = password


@app.before_request
def require_login():
    allowed_routes = ["login", "register"]
    print(session)
    if request.endpoint not in allowed_routes and "username" not in session:
        return redirect("/login")


@app.route("/", methods=["POST", "GET"])
def index():
    title_error = ""
    body_error = ""
    posts = Post.query.all()
    if request.method == "POST":
        post_title = request.form["post-title"]
        post_body = request.form["new-post"]
        owner = User.query.filter_by(username=session["username"]).first()

        if post_title == "" or post_body == "":
            if post_title == "":
                title_error = "Must have a title."

            if post_body == "":
                body_error = "Must have a blog post"

            return render_template("add-post.html", title="Blogz",
                                   title_error=title_error, body_error=body_error, post_title=post_title, post_body=post_body)

        new_post = Post(post_title, post_body,owner)
        db.session.add(new_post)
        db.session.commit()
        new_post_id = new_post.id

    posts = Post.query.all()

    return render_template("posts.html", title="Blogz Post List", posts=posts,
                           title_error=title_error, body_error=body_error)


@app.route("/home", methods=["POST", "GET"])
def homepage(): 
    usernames = User.query.all()
    posts = Post.query.all()
    return render_template("home.html", title="Blogz Homepage", usernames=usernames, posts = posts)


@app.route("/signup", methods=['POST', 'GET'])
def register():
    username = ""
    username_error = ""
    password_error = ""
    verify_error = ""
    if request.method == "POST":
        username = request.form["username"]
        password = request.form["password"]
        verify = request.form["verify"]
        username_error = ""
        password_error = ""
        verify_error = ""

        if password == "":
            password_error = "Password cannot be blank. "

        elif len(password) < 3 or len(password) > 20:
            password = ""
            verify = ""
            password_error = password_error + \
                "Password must be between 3 and 20 characters in length. "

        if verify == "":
            verify_error = "Password cannot be blank. "

        if " " in username:
            username_error = username_error + "Username cannot contain spaces. "

        if " " in password:
            password = ""
            verify = ""
            password_error = password_error + "Password cannot contain spaces. "

        if password != verify:
            password = ""
            verify = ""
            verify_error = verify_error + "Passwords don't match"

        if not username_error and not password_error and not verify_error:

            existing_user = User.query.filter_by(username=username).first()

            if not existing_user:
                new_user = User(username, password)
                db.session.add(new_user)
                db.session.commit()
                session["username"] = username
                return redirect("/add-post")
            else:
                username_error = username_error + " Duplicate user"

    return render_template("register.html", username_error=username_error, password_error=password_error, verify_error=verify_error, username=username)


@app.route('/login', methods=['POST', 'GET'])
def login():
    username = ""
    username_error = ""
    password_error = ""

    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        user = User.query.filter_by(username = username).first()

        if not user:
            username_error = "User does not exist."
            if username == "":
                username_error = "Enter your username."

        if password == "":
            password_error = "Enter your password."

        if user and user.password != password:
            password_error = "Incorrect password."

        if user and user.password == password:
            session['username'] = username
            return redirect('/add-post')
    else: 
        return render_template('login.html') 

    return render_template('login.html', username = username, username_error = username_error, password_error = password_error)


@app.route("/logout")
def logout():
    del session["username"]
    return redirect('/')


@app.route("/view-post", methods=["POST", "GET"])
def view_post():
    post_id = request.args.get("post")
    post = Post.query.get(int(post_id))
    post_title = post.title
    post_body = post.body

    return render_template("view-post.html", post_body=post_body, post_title=post_title)


@app.route("/add-post", methods=["POST", "GET"])
def add_post():
    post_title = ""
    post_body = ""
    title_error = ""
    body_error = ""
    posts = Post.query.all()
    if request.method == "POST":
        post_title = request.form["post-title"]
        post_body = request.form["new-post"]
        owner = User.query.filter_by(username=session["username"]).first()

        if post_title == "" or post_body == "":
            if post_title == "":
                title_error = "Must have a title."

            if post_body == "":
                body_error = "Wheres the post!?"

            return render_template("add-post.html", title="Build a Blog",
                                   title_error=title_error, body_error=body_error, post_title=post_title, post_body=post_body)

        new_post = Post(post_title, post_body, owner)
        db.session.add(new_post)
        db.session.commit()
        new_post_id = new_post.id
        return redirect(f"/view-post?post={new_post_id}")
    return render_template("add-post.html", title="Build a Blog",
                           title_error=title_error, body_error=body_error)


@app.route("/blog")
def blog():
    user_id = request.args.get("user")
    posts = Post.query.filter_by(owner_id=user_id).all()
    username = User.query.filter_by(id=user_id).first()

    return render_template("blog.html", posts=posts, username=username.username)


if __name__ == "__main__":
    app.run()