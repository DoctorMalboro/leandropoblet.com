#-*- encoding: utf-8 -*-
#!/usr/bin/python

# database.py
import hashlib, datetime
from settings import db, Base
from utils import slugify
from wtforms import Form, TextField, TextAreaField, validators
from sqlalchemy.orm import relationship, backref

class User(Base):
    __tablename__ = 'user'
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), unique=True)
    password = db.Column(db.String(60))
    email = db.Column(db.String(120), unique=True)
    is_staff = db.Column(db.Boolean)
    children = relationship('Post', cascade="all, delete, merge")
    
    def __init__(self, email, username, password, is_staff=False):
        self.email = email
        self.username = username
        self.password = hashlib.md5(password).hexdigest()
        
    def __unicode__(self):
        return self.username
        
    def __repr__(self):
        return '<%d: %s (%s)>' % (self.id, self.username, self.email)

class Category(Base):
    __tablename__ = 'category'
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), unique=True)
    desc = db.Column(db.Text)
    children = relationship('Post', cascade="all, delete, merge")
    
    def __init__(self, name, desc=None):
        self.name = name
        self.desc = desc
        
    def __unicode__(self):
        return self.name

class Post(Base):
    __tablename__ = 'post'
    id = db.Column(db.Integer, primary_key=True)
    author = db.Column(db.String(80), db.ForeignKey('user.username'))
    title = db.Column(db.String(80), unique=True)
    content = db.Column(db.Text)
    creation = db.Column(db.DateTime)
    tags = db.Column(db.String(80))
    slug = db.Column(db.String(100))
    category = db.Column(db.String(100), db.ForeignKey('category.name'))
    
    def __init__(self, title, content, author, creation, tags, slug, category):
        self.title = title
        self.content = content
        self.author = db_session.query(User).filter_by(username=author).first()
        self.author = self.author.username
        self.creation = datetime.datetime.now()
        self.tags = tags
        self.slug = slugify(self.title)
        self.category = category
        
    def __unicode__(self):
        return self.slug

# Not really a database, but I don't want to create a whole file just for this little piece of code
class Contact(Form):
    name = TextField('Nombre', [validators.Length(min=5, max=30),
                     validators.Required()])
    email = TextField('Email', [validators.Length(min=10, max=40),
                      validators.Required()])
    subject = TextField('Asunto', [validators.Length(max=20)])
    text = TextAreaField('Mensaje', [validators.Required()])