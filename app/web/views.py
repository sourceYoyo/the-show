
# coding: utf-8
from flask import Flask,render_template
from flask.ext.login import login_required


from . import web
from . import config

@web.route("/")
@web.route("/page/<int:page>")
@login_required
def index():
    return render_template('index.html',user=config.user,site=config.site)

@web.route("/archive")
@login_required
def show_archive_list():
    return render_template("archive_list.html", site=site, pages=pages, posts=posts, created_time=created_time)
    
    
@web.route("/article/<string:article_name>")
@login_required
def getArticleById(article_name):
    return "atticle name is "+article_name
