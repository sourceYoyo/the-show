# coding: utf-8
import math
from datetime import datetime
import json
import os
import random
import re
from flask import *
from flask.ext.login import login_required, current_user
from mongoengine import NotUniqueError

from . import admin
from .forms import *
from ..modules import Category, User, Options, Content


def checkAdmin():
    if current_user.group == 'administrator':
        return True
    else:
        return False

def checkReader():
    if current_user.group == 'reader':
        return True
    else:
        return False

    

@admin.route("/")
@admin.route("/main")
@login_required
def main():
    # 后台概要页面， 获取文章总数及网站设置内容
    if checkReader():
        return redirect('/')
    post_nums = Content.objects(type="post").count()
    return render_template("main.html", post_nums=post_nums, current_user=current_user)



def gen_rnd_filename():
    filename_prefix = datetime.now().strftime('%Y%m%d%H%M%S')
    return '%s%s' % (filename_prefix, str(random.randrange(1000, 10000)))

ALLOWED_EXTENSIONS = set(['png', 'jpg', 'jpeg', 'gif'])
def allowed_file(filename):
    return '.' in filename and filename.rsplit('.',1)[-1] in ALLOWED_EXTENSIONS

@admin.route('/imgupload/', methods=['POST', 'OPTIONS'])
@login_required
#保存上传图片、返回上传图片的相对url
def ckupload():
    """CKEditor file upload"""
    error = ''
    url = ''
    callback = request.args.get("CKEditorFuncNum")

    if request.method == 'POST' and 'upload' in request.files:
        fileobj = request.files['upload']
        fname, fext = os.path.splitext(fileobj.filename)
        rnd_name = '%s%s' % (gen_rnd_filename(), fext)
        if not allowed_file(rnd_name):
            return "攻击失败"
        filepath = os.path.join(admin.static_folder, 'upload', rnd_name)

        # 检查路径是否存在，不存在则创建
        dirname = os.path.dirname(filepath)
        if not os.path.exists(dirname):
            try:
                os.makedirs(dirname)
            except:
                error = 'ERROR_CREATE_DIR'
        elif not os.access(dirname, os.W_OK):
            error = 'ERROR_DIR_NOT_WRITEABLE'

        if not error:
            fileobj.save(filepath)
            url = url_for('static', filename='%s/%s' % ('upload', rnd_name))
    else:
        error = 'post error'

    res = """<script type="text/javascript">
  window.parent.CKEDITOR.tools.callFunction(%s, '%s', '%s');
</script>""" % (callback, url, error)

    response = make_response(res)
    response.headers["Content-Type"] = "text/html"
    return response

# 编写、修改文章
@admin.route("/write-post/cid/<cid>")
@admin.route("/write-post/", methods=["GET", "POST"])
@login_required
def write_post(cid=None):
    if checkReader():
        return redirect('/')
    # url_for("admin.write_post", cid=post.id) ==> url?cid=56d30e9117a6030e248d007a
    # 为了兼容只能这么处理
    if request.args.get("cid"):
        cid = request.args.get("cid")

    # 创建 form 表单内容
    if cid:
        # 存在 cid 说明是在修改文章，将文章内容绑定到 form 表单中
        post = Content.objects(id=cid).first()
        form = postForm(post)
    else:
        # 不存在则设置默认样式
        form = postForm()
    # 为 category 表单赋值选择项
    categories = Category.objects()
    form.category.choices = [(cat.slug, cat.name) for cat in categories]
    form.level.choices=[('low',u'低'),('mid',u'中'),('high',u'高')]

    # 处理保存草稿及发布文章
    if form.validate_on_submit():
        # 根据表单提交的 content_id 判断是否新建或者是修改文章
        # 这里再次判断是否是修改文章的原因是 form 表单提交的地址 cid 永远为 None
        # 所以无法通过 cid 来判断是否是修改文章
        if form.content_id.data:
            post = Content.objects(id=form.content_id.data).first()
        else:
            post = Content(type="post")
        post.set_val(form, session["username"], request.form['ckeditor_content'], "post")

        if request.form["submit"] == "save":
            post.status = False
            try:
                post.save()
          #      response = form.upload(endpoint=admin)
                #ckupload(request)
            except NotUniqueError:
                flash(u"slug 已存在，请修改后再保存", "warning")
                return render_template("write-post.html", form=form, current_user=current_user)
            flash(u"保存草稿成功", "success")
            return redirect(url_for("admin.write_post", cid=post.id))
        else:
            post.status = True
            try:
                post.save()
         #       response = form.upload(endpoint=admin)
                #ckupload(request)
            except NotUniqueError:
                flash(u"slug 已存在，请更改在发布", "warning")
                return render_template("write-post.html", form=form, current_user=current_user)
            flash(u"发布文章成功", "success")
            return redirect(url_for("admin.manage_posts"))

    return render_template("write-post.html", form=form, current_user=current_user)



@admin.route("/show-posts")
@login_required
def show_posts(page=1):
    if checkReader():
        return redirect('/')
    category_name = request.args.get("category")
    if category_name:
        category_name = Category.objects(name=category_name).first()
        posts = Content.objects(type="post", category=category_name)[(page - 1) * 5: page * 5]
    else:
        posts = Content.objects(type="post")[(page - 1) * 5: page * 5]

    pageinate = Content.objects(type="post").paginate(page=page, per_page=5)
    categories = Category.objects()
    createds = []
    delays = []  # 格式化文章发布时间
    comment_count = []
    for post in posts:
        createds.append(post.created.strftime("%Y-%m-%d"))
        delay = math.ceil((datetime.now() - post.created).seconds / 60)
        delays.append(delay)
        comment_count.append(len(post.comments))
    return render_template("app.html", posts=posts, categories=categories,
                           delays=delays, createds=createds, comment_count=comment_count,
                           pageinate=pageinate, current_user=current_user)
# 管理文章
@admin.route("/manage-posts")
@admin.route("/manage-posts/page/<int:page>")
@login_required
def manage_posts(page=1):
    # 存在 category 参数说明是在按照分类筛选文章
    if checkReader():
        return redirect('/')
    category_name = request.args.get("category")
    if category_name:
        category_name = Category.objects(name=category_name).first()
        posts = Content.objects(type="post", category=category_name)[(page - 1) * 5: page * 5]
    else:
        posts = Content.objects(type="post")[(page - 1) * 5: page * 5]

    pageinate = Content.objects(type="post").paginate(page=page, per_page=5)
    categories = Category.objects()
    createds = []
    delays = []  # 格式化文章发布时间
    comment_count = []
    for post in posts:
        createds.append(post.created.strftime("%Y-%m-%d"))
        delay = math.ceil((datetime.now() - post.created).seconds / 60)
        delays.append(delay)
        comment_count.append(len(post.comments))
    return render_template("manage-posts.html", posts=posts, categories=categories,
                           delays=delays, createds=createds, comment_count=comment_count,
                           pageinate=pageinate, current_user=current_user)


# 删除文章
@admin.route("/delete-posts", methods=["POST"])
@login_required
def delete_posts():
    if checkReader():
        return redirect('/')
    cids = request.form.getlist('cid')
    for cid in cids:
        post = Content.objects(id=cid)
        post.delete()
    flash(u"文章删除成功", "success")
    return redirect(url_for('admin.manage_posts'))


# 编写、修改页面
@admin.route("/write-page", methods=["GET", "POST"])
@admin.route("/write-page/cid/<cid>")
@login_required
def write_page(cid=None):
    if checkReader():
        return redirect('/')
    # 兼容性写法
    if request.args.get("cid"):
        cid = request.args.get("cid")

    # 创建 form 表单内容
    if cid:
        # 存在 cid 说明是在修改页面，将文章内容绑定到 form 表单中
        page = Content.objects(id=cid).first()
        form = pageForm(page)
    else:
        form = pageForm()

    if form.validate_on_submit():
        if form.content_id.data:
            page = Content.objects(id=form.content_id.data).first()
        else:
            page = Content(type="page")
        page.set_val(form, session["username"], request.form['edit-area-html-code'], "page")

        if request.form["submit"] == "save":
            page.status = False
            try:
                page.save()
            except NotUniqueError:
                flash(u"slug 已存在，请修改后再保存", "warning")
                return render_template("write-page.html", form=form)
            flash(u"保存草稿成功", "success")
            return redirect(url_for("admin.write_page", cid=page.id))
        else:
            page.status = True
            try:
                page.save()
            except NotUniqueError:
                flash(u"slug 已存在，请修改后再发布", "warning")
                return render_template("write-page.html", form=form)
            flash(u"发布页面成功", "success")
            return redirect(url_for("admin.manage_pages"))
    return render_template("write-page.html", form=form)


# 管理页面
@admin.route("/manage-pages")
@admin.route("/manage-pages/page/<int:page>")
@login_required
def manage_pages(page=1):
    if checkReader():
        return redirect('/')
    pages = Content.objects(type="page")[(page - 1) * 5: page * 5]
    pageinate = Content.objects(type="page").paginate(page=page, per_page=5)
    createds = []  # 格式化页面创建时间
    comment_num = []
    for page in pages:
        createds.append(page.created.strftime("%Y-%m-%d"))
        comment_num.append(len(page.comments))
    return render_template("manage-pages.html", pages=pages, pageinate=pageinate, createds=createds,
                           comment_num=comment_num, current_user=current_user)


# 删除页面
@admin.route('/delete-pages', methods=["POST"])
@login_required
def delete_pages():
    if checkReader():
        return redirect('/')
    cids = request.form.getlist('cid')
    for cid in cids:
        page = Content.objects(id=cid)
        page.delete()
    flash(u"页面删除成功", "success")
    return redirect(url_for('admin.manage_pages'))


# 管理分类
@admin.route("/manage-categories/")
@admin.route("/manage-categories/page/<int:page>")
@login_required
def manage_categories(page=1):
    if checkReader():
        return redirect('/')
    keyword = request.args.get("keyword")
    if keyword:
        categories = Category.objects.search_text(keyword)
    else:
        categories = Category.objects[(page - 1) * 5: page * 5]
    pageinate = Category.objects.paginate(page=page, per_page=5)
    count = [Content.objects(category=category).count() for category in categories]
    return render_template("manage-categories.html", categories=categories, count=count, pageinate=pageinate,
                           current_user=current_user)


# 新建分类
@admin.route("/category", methods=["GET", "POST"])
@admin.route("/category/cid/<cid>")
@login_required
def category(cid=None):
    if checkReader():
        return redirect('/')
    if cid is not None:
        category = Category.objects(id=cid).first()
        form = categoryForm(category)
    else:
        form = categoryForm()

    if form.validate_on_submit():
        if form.category_id.data:
            category = Category.objects(id=form.category_id.data).first()
        else:
            category = Category()
        category.set_val(form)
        category.save()
        flash(u"分类保存成功", "success")
        return redirect(url_for("admin.manage_categories"))

    return render_template("categories.html", form=form, current_user=current_user)


# 删除分类
@admin.route("/delete-categories", methods=["POST"])
@login_required
def delete_categories():
    if checkReader():
        return redirect('/')
    cids = request.form.getlist('cid')
    for cid in cids:
        category = Category.objects(id=cid)
        category.delete()
    flash(u"分类删除成功", "success")
    return redirect(url_for('admin.manage_categories'))


# 新增用户
@admin.route("/users", methods=["GET", "POST"])
@admin.route("/users/cid/<cid>")
@login_required
def users(cid=None):
    if not checkAdmin():
        return redirect(url_for('admin.main'))
    if cid:
        change_user = User.objects(id=cid).first()
        form = userForm(change_user)
    else:
        form = userForm()

    if form.validate_on_submit():
        if form.user_id.data:
            user = User.objects(id=form.user_id.data).first()
        else:
            user = User()
        user.set_and_save(form)
        flash(u"用户添加成功", "success")
        return redirect(url_for("admin.manage_users"))
    return render_template("users.html", form=form, current_user=current_user)


# 管理用户
@admin.route("/manage-users", methods=["GET", "POST"])
@admin.route("/manage-users/page/<page>")
@login_required
def manage_users(page=1):
    if not checkAdmin():
        return redirect(url_for('admin.main'))
    users = User.objects[(page - 1) * 5: page * 5]
    pageinate = User.objects.paginate(page=page, per_page=5)
    return render_template("manage-users.html", users=users, pageinate=pageinate, current_user=current_user)


# 删除用户
@admin.route("/delete-users", methods=["GET", "POST"])
@login_required
def delete_users():
    if not checkAdmin():
        return redirect(url_for('admin.main'))
    uids = request.form.getlist('uid')
    for uid in uids:
        user = User.objects(id=uid).first()
        if user.username == session['username']:
            flash("禁止删除正在登录的用户", "danger")
            return redirect(url_for('admin.manage_users'))
        else:
            user.delete()
    flash(u"用户删除成功", "success")
    return redirect(url_for('admin.manage_users'))




# 网站信息管理
@admin.route('/options-general', methods=["GET", "POST"])
@login_required
def options_general():
    if not checkAdmin():
        return redirect(url_for('admin.main'))
    if request.method == "GET":
        option = Options.objects.first()
        form = OptionGeneralForm(option)
        return render_template("options-general.html", form=form, current_user=current_user)

    form = OptionGeneralForm()
    if form.validate_on_submit():
        option = Options.objects.first()
        option.set_and_save(form)
        flash(u"网站信息保存成功", "success")
        return redirect(url_for("admin.options_general"))

