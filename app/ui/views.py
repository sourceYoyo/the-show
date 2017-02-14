# coding: utf-8
from flask import render_template

from app.modules import Options, Content, Category
from . import ui
from flask.ext.login import login_fresh,login_required



# 主页， 附带页码
@ui.route("/")
@ui.route("/page/<int:page>")
@login_required
def index(page=1):
    site = Options.objects().first()
    posts = Content.objects(type="post", status=True)[(page - 1) * 5: page * 5]
    pages = Content.objects(type="page", status=True)
    pagination = Content.objects(type="post", status=True).paginate(page=page, per_page=5)
    return render_template("index.html", site=site, posts=posts, pages=pages, pagination=pagination)


# 查看页面
@ui.route("/<slug>")
@login_required
def show_page(slug):
    site = Options.objects().first()
    pages = Content.objects(type="page", status=True)
    page = Content.objects(slug=slug).first()
    return render_template("page.html", site=site, pages=pages, page=page)


# 查看文章
@ui.route("/post/<slug>")
@login_required
def show_post(slug):
    logined = 0
    if login_fresh():
        logined=1
    site = Options.objects().first()
    pages = Content.objects(type="page", status=True)
    post = Content.objects(slug=slug).first()
    return render_template("post.html", site=site, pages=pages, post=post,logined=logined)


# 查看归档目录
@ui.route("/archive")
@login_required
def show_archive_list():
    site = Options.objects().first()
    pages = Content.objects(type="page", status=True)
    posts = Content.objects(type="post", status=True)
    created_time = []
    for post in posts:
        created_time.append(post.created.strftime("%Y-%m-%d"))

    return render_template("archive_list.html", site=site, pages=pages, posts=posts, created_time=created_time)


# 查看分类下所有文章
@ui.route("/category/<slug>")
@ui.route("/categort/<slug>/page/<int:page>")
@login_required
def show_category(slug, page=1):
    site = Options.objects().first()
    pages = Content.objects(type="page", status=True)
    category = Category.objects(slug=slug).first()
    title = '分类 "%s" 下的文章' % (category.name)
    posts = Content.objects(category=category, status=True)[(page - 1) * 5: page * 5]
    pagination = Content.objects(category=category, status=True).paginate(page=page, per_page=5)
    created_time = []
    for post in posts:
        created_time.append(post.created.strftime("%Y-%m-%d"))

    return render_template('archive.html', title=title, posts=posts, created_time=created_time, site=site, pages=pages,
                           pagination=pagination, slug=slug)


# 查看标签下所有文章
@ui.route("/tag/<slug>")
@ui.route("/tag/<slug>/page/<int:page>")
@login_required
def show_tag(slug, page=1):
    site = Options.objects().first()
    pages = Content.objects(type="page", status=True)
    title = '标签 "%s" 下的文章' % slug
    posts = Content.objects(tags=slug, status=True)[(page - 1) * 5: page * 5]
    pagination = Content.objects(tags=slug, status=True).paginate(page=page, per_page=5)
    created_time = []
    for post in posts:
        created_time.append(post.created.strftime("%Y-%m-%d"))

    return render_template('archive.html', title=title, posts=posts, created_time=created_time, site=site, pages=pages,
                           pagination=pagination, slug=slug)
