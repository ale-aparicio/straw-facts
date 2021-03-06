import os
import json
from flask import (
    Flask, flash, render_template,
    redirect, request, session, url_for)
from flask_pymongo import PyMongo
from bson.objectid import ObjectId
from werkzeug.security import generate_password_hash, check_password_hash
if os.path.exists("env.py"):
    import env


app = Flask(__name__)

app.config["MONGO_DBNAME"] = os.environ.get("MONGO_DBNAME")
app.config["MONGO_URI"] = os.environ.get("MONGO_URI")
app.secret_key = os.environ.get("SECRET_KEY")

mongo = PyMongo(app)


@app.route("/")
def index():
    data = []
    with open("data/theories.json", "r") as json_data:
        data = json.load(json_data)
    return render_template(
        "index.html",
        theories=data
    )


# Function to register for the register.html page


@app.route("/register", methods=["GET", "POST"])
def register():
    if request.method == "POST":
        # Check if username already exists in db
        existing_user = mongo.db.users.find_one(
            {"username": request.form.get("username").lower()})

        if existing_user:
            flash("Username already exists")
            return redirect(url_for("register"))

        register = {
            "username": request.form.get("username").lower(),
            "password": generate_password_hash(request.form.get("password"))
        }
        mongo.db.users.insert_one(register)

        # put the new user into 'session' cookie
        session["user"] = request.form.get("username").lower()
        flash("Registration Successful!")
        return redirect(url_for("profile", username=session["user"]))

    return render_template("register.html")


# Function to log in for the login.html page


@app.route("/login", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        # Check if username exists in db
        existing_user = mongo.db.users.find_one(
            {"username": request.form.get("username").lower()})

        if existing_user:
            # ensure hashed password matches user input
            if check_password_hash(
                    existing_user["password"], request.form.get("password")):
                session["user"] = request.form.get("username").lower()
                flash("Welcome, {}".format(
                    request.form.get("username")))
                return redirect(url_for(
                    "profile", username=session["user"]))
            else:
                # invalid password match
                flash("Incorrect Username and/or Password")
                return redirect(url_for("login"))

        else:
            # If User doesn't exist
            flash("Incorrect Username and/or Password")
            return redirect(url_for("login"))

    return render_template("login.html")


@app.route("/profile/<username>", methods=["GET", "POST"])
def profile(username):
    # Get the session's username from database
    username = mongo.db.users.find_one(
        {"username": session["user"]})["username"]

    if session["user"]:
        originals = mongo.db.theories.find()
        return render_template(
            "profile.html",
            username=username,
            originals=originals
        )

    return render_template(
        "profile.html",
        username=username,
        originals=originals
    )


@app.route("/logout")
def logout():
    # Remove user from session cookies
    flash("You have been logged out")
    session.pop("user")
    return redirect(url_for("login"))


# Route for the Theories page connected to the respective Json data page


@app.route("/theories")
def theories():
    data = []
    with open("data/theories.json", "r") as json_data:
        data = json.load(json_data)
    return render_template(
        "theories.html",
        page_title="Theory",
        theories=data
    )


# Route for the Sub Theories connected to the MongoDB database


@app.route("/world_theories")
def world_theories():
    worlds = mongo.db.theories.find()
    return render_template(
        "world_theories.html",
        page_title="World Theories",
        worlds=worlds
        )


@app.route("/character_theories")
def character_theories():
    characters = mongo.db.theories.find()
    return render_template(
        "character_theories.html",
        page_title="Character Theories",
        characters=characters
        )


@app.route("/fruit_theories")
def fruit_theories():
    fruits = mongo.db.theories.find()
    return render_template(
        "fruit_theories.html",
        page_title="Fruit Theories",
        fruits=fruits
        )


@app.route("/story_theories")
def story_theories():
    stories = mongo.db.theories.find()
    return render_template(
        "story_theories.html",
        page_title="Story Theories",
        stories=stories
        )


@app.route("/crew_theories")
def crew_theories():
    crews = mongo.db.theories.find()
    return render_template(
        "crew_theories.html",
        page_title="Crew Theories",
        crews=crews
        )


@app.route("/misc_theories")
def misc_theories():
    miscs = mongo.db.theories.find()
    return render_template(
        "misc_theories.html",
        page_title="Mischellaneous Theories",
        miscs=miscs
        )


# Function to add a theory


@app.route("/add_theories", methods=["GET", "POST"])
def add_theories():
    if request.method == "POST":
        theory = {
            "category": request.form.get("category"),
            "title": request.form.get("title"),
            "created_by": session["user"],
            "content": request.form.get("content")
        }
        mongo.db.theories.insert_one(theory)
        flash("Theory Sucessfully Added")
        return redirect(url_for("theories"))

    categories = mongo.db.categories.find().sort("category", 1)
    # Route for the categories selection into the theories.json
    return render_template(
        "add_theory.html", page_title="Create a Theory",
        categories=categories
        )


# Function to edit a theory


@app.route("/edit_theories/<theory_id>", methods=["GET", "POST"])
def edit_theories(theory_id):
    if request.method == "POST":
        submit = {
            "category": request.form.get("category"),
            "title": request.form.get("title"),
            "created_by": session["user"],
            "content": request.form.get("content")
        }
        mongo.db.theories.update({"_id": ObjectId(theory_id)}, submit)
        flash("Theory Successfully Updated")
        return redirect(url_for("theories"))

    content = mongo.db.theories.find_one({"_id": ObjectId(theory_id)})
    categories = mongo.db.categories.find().sort("category", 1)
    return render_template(
        "edit_theory.html",
        page_title="Edit a Theory",
        content=content,
        categories=categories
    )


# Function to delete a theory


@app.route("/delete_theories/<theory_id>")
def delete_theories(theory_id):
    mongo.db.theories.remove({"_id": ObjectId(theory_id)})
    flash("Theory Successfully Deleted")
    return redirect(url_for("theories"))


# remember to change debug = true to false


if __name__ == "__main__":
    app.run(
        host=os.environ.get("IP"),
        port=int(os.environ.get("PORT")),
        debug=False
        )
