#!/usr/bin/env python
#-*- coding: utf-8 -*-
import sys
reload(sys)
from flask.ext.script import Manager, Shell

import os

sys.setdefaultencoding('utf-8')

from app import create_app
from app.install import install
from app.modules import User, Content, Category, Comment, Options


if os.name == "posix":
    FLASK_CONFIG = "product"
else:
    FLASK_CONFIG = "develop"

app = create_app(FLASK_CONFIG)


if __name__=='__main__':
	app.run(host='0.0.0.0')
