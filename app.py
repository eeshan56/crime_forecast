from flask import Flask, render_template, redirect, request, url_for, flash, session
from form import RegistrationForm, LoginForm
from pymongo import MongoClient
from passlib.hash import sha256_crypt
from datetime import timedelta


#def isLogIn():
	#return True
	#return False

app = Flask(__name__)
app.secret_key = '0f728c6b5c9f6e02690f9496da4818ae'
app.permanent_session_lifetime = timedelta(days = 1)

@app.route("/")
@app.route("/home")
def home():
	return render_template('index.html')

# Ensure responses aren't cached
@app.after_request
def after_request(response):
    response.headers["Cache-Control"] = "no-cache, no-store, must-revalidate"
    return response

@app.route("/about")
def about():
	return render_template('about.html', title = 'About')

@app.route("/profile")
def profile():
	if 'username' in session and 'email' in session:
		return render_template('profile.html', title = 'My Profile')
	else:
		return redirect(url_for('login'))

@app.route("/logout")
def logout():
	if 'username' in session and 'email' in session:
		session.pop('username', None)
		session.pop('email', None)
		flash('Logged out successfully!', 'success')
		#logged_in = False
	return redirect(url_for('home'))

@app.route("/map")
def map():
	if 'username' in session and 'email' in session:
		print("In map")
	else:
		return redirect(url_for('login'))
	return render_template('map.html', title = 'Map')

@app.route("/forgot")
def forgot():
	return render_template('forgot.html')

@app.route("/login", methods = ['GET', 'POST'])
def login():
	#if logged_in:
		#print("I'm here")
		#flash('You are already logged in', 'success')
		#return redirect(url_for('home'))
	form = LoginForm()
	if request.method == 'POST':
		if form.validate_on_submit():
			client = MongoClient("mongodb+srv://test:test123%23@cluster0-l5ord.mongodb.net/test?retryWrites=true&w=majority")
			db = client.get_database('user_db')
			creds = db.user_creds
			find_user = list(creds.find({'email':form.email.data}))
			if len(find_user) == 1:
				if sha256_crypt.verify(form.password.data, find_user[0]['passwd']):
					session['email'] = form.email.data
					session['username'] = find_user[0]['username']
					flash('Welcome ' + session['username'] + '!', 'success')
					#logged_in = True
					session.permanent = True
					return redirect(url_for('map'))
				else:
					flash('Please enter the correct email or password', 'danger')
			else:
				flash('Please enter the correct email or password', 'danger')
	else:
		if "username" in session and "email" in session:
			flash("You're already logged in", 'success')
			return redirect(url_for("home"))
	return render_template('login.html', title = 'Login', form = form)

@app.route("/register", methods = ['GET', 'POST'])
def register():
	#if logged_in:
		#flash('You are already logged in', 'success')
		#return redirect(url_for('home'))
	form = RegistrationForm()
	if request.method == "POST":
		if form.validate_on_submit():
			client = MongoClient("mongodb+srv://test:test123%23@cluster0-l5ord.mongodb.net/test?retryWrites=true&w=majority")
			db = client.get_database('user_db')
			creds = db.user_creds
			dup_user = list(creds.find({'username' : form.username.data}))
			dup_email = list(creds.find({'email' : form.email.data}))

			if len(dup_user) == 0 and len(dup_email) == 0:
				enc_pass = sha256_crypt.encrypt(form.password.data)
				new_user = {'username' : form.username.data, 'email' : form.email.data, 'passwd' : enc_pass}
				creds.insert_one(new_user)
				session['email'] = form.email.data
				session['username'] = form.username.data
				flash(f'Account created for {form.username.data}!', 'success')
				#logged_in = True
				session.permanent = True
				return redirect(url_for('map'))
			elif len(dup_user) == 0:
				flash(f'{form.email.data} is already in use', 'danger')
			else:
				flash(f'{form.username.data} is already in use', 'danger')
	else:
		if "username" in session and "email" in session:
			flash("You're already logged in", 'success')
			return redirect(url_for('home'))
	return render_template('register.html', title = 'Register', form = form)



if __name__ == '__main__':
	#logged_in = False
	app.run(host = '0.0.0.0', debug = True)