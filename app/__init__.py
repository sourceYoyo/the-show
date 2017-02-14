#-*- coding: utf-8 -*-
import urllib2
import pymongo
from flask import Flask, request,Blueprint,render_template
from flask import *
from .map import wifi_blue,saveFromFile
from flask_login import *

from .sharedb import *
from flask import *	
from flask.ext.bootstrap import Bootstrap
from flask.ext.mongoengine import MongoEngine
from flask.ext.login import LoginManager,login_required
from flask.ext.wtf import CsrfProtect
from config import config


bootstrap = Bootstrap()
csrf = CsrfProtect()
login_manager = LoginManager()
login_manager.session_protection = "strong"
login_manager.login_view = "auth.login"
login_manager.login_message_category = "warning"
login_manager.login_message = u"您必须登录后才能访问这个页面"
db = MongoEngine()

app = Flask(__name__)


def create_app(config_name):
    app.config.from_object(config[config_name])
    config[config_name].init_app(app)

    bootstrap.init_app(app)
    csrf.init_app(app)
    login_manager.init_app(app)
    db.init_app(app)

    #定时任务
    import jobs

    # 导入用户验证模块
    from .auth import auth as auth_blueprint
    from .admin import admin as admin_blueprint
    from .ui import ui as ui_blueprint
    from .data import data_blue
    from .main import main_blue
    app.register_blueprint(auth_blueprint, url_prefix="/auth")
    app.register_blueprint(admin_blueprint, url_prefix="/admin")
    app.register_blueprint(wifi_blue, url_prefix='/wifi')
    app.register_blueprint(data_blue, url_prefix='/data')
    app.register_blueprint(main_blue, url_prefix='')
    app.register_blueprint(ui_blueprint)
    app.debug=True
    return app
