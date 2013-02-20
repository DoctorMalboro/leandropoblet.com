import os, hashlib
from settings import db_session, app, mail, user_session
from database import User, Category, Post, Contact
from utils import login_required
from urlparse import urljoin
from flask import render_template, session, request, redirect, url_for

@app.route('/')
def index():
    check_login = user_session['username']
    return render_template('index.html',
    	check_login=check_login)
    
@app.route('/bio/')
def bio():
    return render_template('bio.html')
    
@app.route('/proyectos/')
def proyects():
    return render_template('projects.html')
    
@app.route('/blog/')
def blog():
	posts = db_session.query(Post).order_by(Post.creation.desc())
	categories = db_session.query(Category).order_by(Category.name.asc())
	return render_template('blog.html',
		posts=posts,
		categories=categories)

@app.route('/contacto/', methods=['GET', 'POST'])
def contact():
    form = Contact(request.form)
    if request.method == 'POST' and form.validate():
        message = 'Nombre: %s\nEmail: %s\n%s' % (form.name.data,
        									form.email.data, form.text.data)
        msg = Message(subject=form.subject.data, sender=form.email.data,
        			  body=message, recipients=[''])
        mail.send(msg)
        return render_template('success.html')
    return render_template('contact-form.html',
    	form=form)

@app.route('/blog/<post_slug>/')
def entry(post_slug):
	post = db_session.query(Post).filter_by(slug=post_slug).first()
	categories = db_session.query(Category).order_by(Category.name.asc())
	if post:
		return render_template('entry.html',
			post=post)
	else:
		return 'Error'

@app.route('/user/<username>/')
def user(username):
	user = db_session.query(User).filter_by(username=username).first()
	user_posts = db_session.query(Post).filter_by(author=username)\
	.order_by(Post.creation.desc())
	if user:
		return render_template('user.html',
			user=user,
			user_posts=user_posts)
	else:
		return 'Error'

@app.route('/blog/category/<name>/')
def category(name):
	category = db_session.query(Category).filter_by(name=name).first()
	post_in_category = db_session.query(Post).filter_by(category=name).all()
	if category:
		return render_template('category.html',
			category=category,
			posts=post_in_category)
	else:
		return 'Error'
		
@login_required
@app.route('/admin/')
def admin():
	if user_session['username'] != '':
		return render_template('admin.html',
				session_username=user_session['username'])
	else:
		return redirect(url_for('login'))
		
@login_required
@app.route('/admin/entry/')
def entry_list():
	if user_session['username'] != '':
		entries = db_session.query(Post).order_by(Post.id.asc())
		return render_template('entry-list.html',
			entries=entries,
			session_username=user_session['username'])
	else:
		return redirect(url_for('login'))
		
@login_required
@app.route('/admin/entry/add/', methods=['GET', 'POST'])
def add_entry():
	if user_session['username'] != '':
		if request.method == 'POST':
			if request.form['title'] == '' or request.form['content'] == ''\
			or request.form['author'] == '' or request.form['slug'] == ''\
			or  request.form['category'] == '':
				return 'Empty fields are not allowed. Try again.'
			else:
				entry = Post(title=request.form['title'].encode('utf-8'),
					content=request.form['content'].encode('utf-8'),
					author=request.form['author'],
					creation=datetime.datetime.now(),
					tags=request.form['tags'],
					slug=request.form['slug'],
					category=request.form['category'])
				db_session.add(entry)
				db_session.commit()
				return redirect(url_for('entry_list'))
	else:
		return redirect(url_for('login'))
			
	categories = db_session.query(Category).all()
	authors = db_session.query(User).all()
	return render_template('add-entry.html',
		categories=categories,
		authors=authors,
		session_username=user_session['username'])

@login_required
@app.route('/admin/entry/edit/<slug>/', methods=['GET', 'POST'])
def edit_entry(slug):
	content = db_session.query(Post).filter_by(slug=slug).first()
	authors = db_session.query(User).all()
	categories = db_session.query(Category).all()
	if request.method == 'POST':
		if request.form['title'] != '' or request.form['content'] != ''\
		or request.form['tags'] != '' or request.form['slug'] != '':
			if content.author == request.form['author']\
			and content.category == request.form['category']:
				db_session.query(Post).filter_by(slug=slug).update(
					{'title': request.form['title'].encode('utf-8'),
					'content': request.form['content'].encode('utf-8'),
					'tags': request.form['tags'],
					'slug': request.form['slug']})
			else:
				db_session.query(Post).filter_by(slug=slug).update(
					{'title': request.form['title'],
					'author': request.form['author'],
					'content': request.form['content'],
					'category': request.form['category'],
					'tags': request.form['tags'],
					'slug': request.form['slug']})
			db_session.commit()
			return redirect(url_for('entry_list'))
	return render_template('edit-entry.html',
		post=content,
		authors=authors,
		categories=categories,
		session_username=user_session['username'])
	
@login_required
@app.route('/admin/entry/delete/<slug>/')
def delete_entry(slug):
    entry = db_session.query(Post).filter_by(slug=slug).first()
    print entry
    if entry != '':
        db_session.delete(entry)
        db_session.commit()
    else:
        return 'The entry does not exist.'
    return redirect(url_for('entry_list'))
			
@login_required
@app.route('/admin/category/')
def category_list():
	if user_session['username'] != '':
		categories = db_session.query(Category).order_by(Category.id.asc())
		return render_template('category-list.html',
			categories=categories,
			session_username=user_session['username'])	
	else:
		return redirect(url_for('login'))

@login_required
@app.route('/admin/category/add/', methods=['GET', 'POST'])
def add_category():
	if user_session['username'] != '':
		if request.method == 'POST':
			if request.form['name'] == '':
				return 'Empty fields are not allowed. Try again.'
			else:
				category = Category(name=request.form['name'].encode('utf-8'),
					desc=request.form['desc'].encode('utf-8'))
				db_session.add(category)
				db_session.commit()
				return redirect(url_for('category_list'))
	else:
		return redirect(url_for('login'))
	return render_template('add-category.html',
		session_username=user_session['username'])
	
@login_required
@app.route('/admin/category/edit/<name>/', methods=['GET', 'POST'])
def edit_category(name):
	if user_session['username'] != '':
		cat_content = db_session.query(Category).filter_by(name=name).first()
		if request.method == 'POST':
			if request.form['name'] != ''\
			and request.form['desc'] == cat_content.desc:
				db_session.query(Category).filter_by(name=name).update(
					{'name': request.form['name'].encode('utf-8')})
			else:
				db_session.query(Category).filter_by(name=name).update(
					{'name': request.form['name'].encode('utf-8'),
					'desc': request.form['desc'].encode('utf-8')}) 
			db_session.commit()
			return render_template(url_for('category_list'))
	else:
		return redirect(url_for('login'))
	return render_template('edit-category.html',
		category=cat_content,
		session_username=user_session['username'])
	
@login_required
@app.route('/admin/category/delete/<name>/')
def delete_category(name):
    cat = db_session.query(Category).filter_by(name=name).first()
    if cat != '':
        db_session.delete(cat)
        db_session.commit()
    else:
        return 'The category does not exist.'
    return redirect(url_for('category_list'))
		
@login_required
@app.route('/admin/user/')
def user_list():
	if user_session['username'] != '':
		users = db_session.query(User).order_by(User.id.asc())
		return render_template('user-list.html',
			users=users,
			session_username=user_session['username'])
	else:
		return redirect(url_for('login'))
		
@login_required
@app.route('/admin/user/add/', methods=['GET', 'POST'])
def add_user():
	if request.method == 'POST':
		if request.form['username'] != '' or request.form['password'] != ''\
		or request.form['email'] != '':
			add_user = User(username=request.form['username'],
				password=request.form['password'],
				email=request.form['email'],
				is_staff=request.form['staff'])
		db_session.add(add_user)
		db_session.commit()
		return redirect(url_for('user_list'))
	return render_template('add-user.html',
		session_username=user_session['username'])
			
@login_required
@app.route('/admin/user/edit/<username>/', methods=['GET', 'POST'])
def edit_user(username):
	user = db_session.query(User).filter_by(username=username).first()
	if request.method == 'POST':
		if request.form['username'] != '' and request.form['email'] != '':
			db_session.query(User).filter_by(username=username).update(
				{'username': request.form['username'],
				'email': request.form['email'],
				'is_staff': request.form['staff']})
		db_session.commit()
		return redirect(url_for('user_list'))
	return render_template('edit-user.html',
		user=user,
		session_username=user_session['username'])

@login_required
@app.route('/admin/user/delete/<username>/')
def delete_user(username):
    user = db_session.query(User).filter_by(username=username).first()
    if user != '':
        db_session.delete(user)
        db_session.commit()
    else:
        return 'The user does not exist.'
    return redirect(url_for('user_list'))

@app.route('/login/', methods=['GET', 'POST'])
def login():
	error = None
	if request.method == 'POST':
		login_username = request.form['username']
		login_password = hashlib.md5(request.form['password']).hexdigest()
		database_username = db_session.query(User)\
		.filter_by(username=login_username).first().username
		database_password = db_session.query(User)\
		.filter_by(username=login_username).first().password
		if database_username == []:
			error = 'Invalid username %s!' % login_username
		elif database_password != login_password:
			error = 'Invalid password!'
		else:
			user_session['username'] = request.form['username']
			return redirect('/admin/')
	return render_template('login.html', error=error)

def make_external(url):
	return urljoin(request.url_root, url)

@app.route('/feed.atom')
def recent_feed():
	feed = AtomFeed('Recientemente en mi blog', 
		feed_url=request.url,
		url=request.url_root)
	articles = db_session.query(Post).order_by(Post.creation.desc())\
	.limit(5).all()
	for article in articles:
		feed.add(article.title,
			article.content.decode('utf-8'),
			content_type='html',
			author=article.author,
			url=make_external(article.title),
			updated=article.creation,
			published=article.creation)
	return feed.get_response()

@login_required
@app.route('/logout/')
def logout():
	user_session['username'] = ''
	return redirect(url_for('index'))
	
@app.errorhandler(404)
def page_not_found(error):
    return render_template('404.html')

@app.route('/error/')
def error_page():
	return render_template('error.html')

if __name__ == '__main__':
	port = int(os.environ.get('PORT', 5000))
	app.run(host='0.0.0.0', port=port, debug=True)
