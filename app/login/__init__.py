#-*- coding: utf-8 -*-
from flask import *
from flask_login import *
from flask_mongoengine import MongoEngine
from flask_security import *

user_blue = Blueprint('user', __name__, url_prefix='/user')

db = MongoEngine()

loginManager = LoginManager()


class User(db.Document):
    name = db.StringField(required=True, max_length=64)
    password = db.StringField(max_length=256)
    description = db.StringField(max_length=1024)

    # Flask-Login integration
    def is_authenticated(self):
        return True

    def is_active(self):
        return True

    def is_anonymous(self):
        return False

    # TypeError: ObjectId('552f41e56a85f00dd043406b') is not JSON serializable
    def get_id(self):
        return str(self.id)

    def __unicode__(self):
        return self.name


@loginManager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))


@user_blue.route("/logout")
@login_required
def logout():
    logout_user()
    return redirect(url_for("index"))

@user_blue.route("/login", methods=["GET","POST"])
def submitLogin():
    user = User()
    user.id=1112
    if 1==1:
	login_user(user)
    return redirect(request.args.get("next") or url_for("/"))

@user_blue.route("/register")
@login_required
def register():

    return redirect(url_for("index"))
