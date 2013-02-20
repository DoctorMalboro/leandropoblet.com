#-*- encoding: utf-8 -*-
#!/usr/bin/python

# Settings.py
import os
import dj_database_url
from flask import Flask
from flask.ext.sqlalchemy import SQLAlchemy
from flask.ext.assets import Environment, Bundle
from flask.ext.mail import Mail, Message
from sqlalchemy import create_engine
from sqlalchemy.orm import scoped_session, sessionmaker
from sqlalchemy.ext.declarative import declarative_base
from werkzeug.contrib.atom import AtomFeed

SECRET_KEY = ''

user_session = {'username': '', 'path': ''}

db_url = ''

app = Flask(__name__)
app.config.update(
	DEBUG = True,
	#EMAIL SETTINGS
	MAIL_SERVER = 'smtp.gmail.com',
	MAIL_PORT = 465,
	MAIL_USE_SSL = True,
	MAIL_USERNAME = '',
	MAIL_PASSWORD = '',
	STATIC_URL = '',
	SQLALCHEMY_DATABASE_URI = dj_database_url.config(),
)

uri = os.environ.get('DATABASE_URL', db_url)
engine = create_engine(uri, convert_unicode=True)
db_session = scoped_session(sessionmaker(autocommit=False,
	autoflush=False,
	bind=engine))

db = SQLAlchemy(app)
Base = declarative_base()

app.config.from_object(__name__)
mail = Mail(app)
assets = Environment(app)
db.init_app(app)

css = Bundle('css/style.css', 'css/skeleton.css')
assets.register('styles', css)
css = Bundle('css/admin.css')
assets.register('admin-styles', css)
