# coding: utf-8
from .modules import Category, Options, User


def install():
    User(username="admin", password="admin", url="thu.admin", screenName="thu",
         group="administrator").save()
    Category(name="默认分类", slug="normal", description="这是系统默认的分类").save()
    Options(url="", title="", keyword="", description="").save()
