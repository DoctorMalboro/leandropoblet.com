#-*- encoding: utf-8 -*-
#!/usr/bin/python

# utils.py
import re
from settings import user_session
from functools import wraps
from flask import redirect, url_for, request

def slugify(title):
	slug_re = re.compile('[a-zA-Z0-9]+')
	
	_title = title[:99].replace(' ', '-')
	return '-'.join(re.findall(slug_re, _title))

def login_required(f):
    @wraps(f)
    def decorator(*args, **kwargs):
        if user_session['username'] == '':
            return redirect(url_for('login'))
        else:
            return redirect('%s?next=%s' % (url_for('login'), request.path))
        return f(*args, **kwargs)
    return decorator