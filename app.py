from flask import Flask, render_template, redirect, request, url_for, flash, session
from form import RegistrationForm, LoginForm, NERForm, ForgotPassword, ResetPassword
from pymongo import MongoClient
from passlib.hash import sha256_crypt
from datetime import timedelta, date, datetime
from urllib.parse import urlencode

import requests
import json
import smtplib
import random
import string

host = '0.0.0.0'

app = Flask(__name__)
app.secret_key = '0f728c6b5c9f6e02690f9496da4818ae'
app.permanent_session_lifetime = timedelta(days = 1)

@app.route("/")
@app.route("/home")
def home():
	if 'admin' in session:
		return redirect(url_for('ad_home'))
	return render_template('index.html')

@app.route("/ad_home")
def ad_home():
	if 'username' in session and 'email' in session and 'admin' in session:
		return render_template('admin_index.html')
	else:
		if 'username' in session and 'email' in session:
			flash("Admin pages aren't accessible to users", 'danger')
			return redirect(url_for('home'))
		else:
			flash("Please use the admin login to access your admin account", 'danger')
	return redirect(url_for('ad_login'))

@app.route("/ad_ner", methods = ['GET', 'POST'])
def ad_ner():
	form = NERForm()
	if 'username' in session and 'email' in session and 'admin' in session:
		if request.method == "POST":
			processed_text = form.text_area.data

			client = MongoClient("mongodb+srv://test:test123%23@cluster0-l5ord.mongodb.net/test?retryWrites=true&w=majority")
			db = client.get_database('user_db')

			article_db = db.articles

			#print(processed_text)

			data = json.dumps({"text" : processed_text})

			#data = '{"text": "Seven young men, armed with sharp weapons, went on the rampage in Nigdi on Friday night."}'

			#print(data)

			#print(data2)

			response = requests.post('http://localhost:5005/model/parse', data = data)

			json_data = json.loads(response.text)

			list_of_entities = json_data['entities']

			new_article = {}
			for j in range(len(list_of_entities)):
				if not str(list_of_entities[j]['entity']) in new_article:
					new_article[str(list_of_entities[j]['entity'])] = list_of_entities[j]['value']

			d = form.date_field.data.strftime('%Y-%m-%d')
			d = d.split("-")
			new_article['Date'] = d[1] + "-" + d[2] + "-" + d[0]

			article_db.insert(new_article)
			flash('Entities extracted', 'success')
			form.text_area.data = ""
			return render_template('admin_ner.html', title = 'NER', form = form)
	else:
		if 'username' in session and 'email' in session:
			flash("Admin pages aren't accessible to users", 'danger')
			return redirect(url_for('home'))
		else:
			flash("Please use the admin login to access your admin account", 'danger')
			return redirect(url_for('ad_login'))

	return render_template('admin_ner.html', title = 'NER', form = form)

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
		return render_template('profile.html', email = session['email'], title = 'My Profile')
	else:
		return redirect(url_for('login'))

@app.route("/logout")
def logout():
	if 'username' in session and 'email' in session:
		session.pop('username', None)
		session.pop('email', None)

		if 'admin' in session:
			session.pop('admin', None)

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

@app.route("/reset_password", defaults = {'email' : ''}, methods = ['GET', 'POST'])
@app.route("/reset_password/<email>", methods = ['GET', 'POST'])
def reset_password(email):
	if email == "":
		if not 'email' in session:
			flash('You need to be logged in to reset your password', 'danger')
			return redirect(url_for('home'))
		else:
			email = session['email']

	form = ResetPassword()

	if request.method == 'POST':

		if form.validate_on_submit():

			client = MongoClient("mongodb+srv://test:test123%23@cluster0-l5ord.mongodb.net/test?retryWrites=true&w=majority")
			db = client.get_database('reset_db')
			creds = db.reset_creds
			reset_doc = list(creds.find({'email_' : email}))
			creds.delete_many({"email_" : email})
			if reset_doc[0]['admin']:

				if sha256_crypt.verify(form.reset.data, reset_doc[0]['code']):

					if (datetime.now() - reset_doc[0]['timestamp']).seconds > 120:

						flash("This code is no longer valid. Click 'Resend Code'", 'danger')

					else:

						dbA = client.get_database('admin_db')
						a_creds = dbA.admin_creds
						admin_guy = admin_creds.find({"email" : email})
						admin_creds.update_one({"email" : email}, {"$set" : {"passwd" : sha256_crypt.encrypt(form.password.data)}})
						
						session['email'] = email
						session['username'] = admin_guy['username']
						session['admin'] = 1

						flash("Password reset successful", 'success')
						return redirect(url_for('map'))
				else:

					flash("Please enter the valid code", 'danger')
			else:

				if sha256_crypt.verify(form.reset.data, reset_doc[0]['code']):

					if (datetime.now() - reset_doc[0]['timestamp']).seconds > 120:

						flash("This code is no longer valid. Click 'Resend Code'", 'danger')

					else:

						dbU = client.get_database('user_db')
						u_creds = dbU.user_creds
						user_guy = list(u_creds.find({"email" : email}))
						u_creds.update_one({"email" : email}, {"$set" : {"passwd" : sha256_crypt.encrypt(form.password.data)}})
						
						session['email'] = email
						session['username'] = user_guy[0]['username']

						flash("Password reset successful", 'success')
						return redirect(url_for('home'))
				else:

					flash("Please enter the valid code", 'danger')

	return render_template('reset_password.html', title = 'Reset Password', email = email, form = form)

@app.route("/resend", defaults = {'email' : ''}, methods = ['GET', 'POST'])
@app.route("/resend/<email>", methods = ['GET', 'POST'])
def resend(email):
	if email == "":
		if 'admin' in session:
			return redirect(url_for('ad_home'))
		else:
			return redirect(url_for('home'))

	client = MongoClient("mongodb+srv://test:test123%23@cluster0-l5ord.mongodb.net/test?retryWrites=true&w=majority")

	db = client.get_database('reset_db')
	dbA = client.get_database('admin_db')
	dbU = client.get_database('user_db')

	creds = db.reset_creds
	a_creds = dbA.admin_creds
	u_creds = dbU.user_creds

	find_user1 = list(u_creds.find({"email" : email}))
	find_user2 = list(a_creds.find({"email" : email}))

	creds.delete_many({"email_" : email})

	reset_code = randomStringDigits(8)
	reset_doc = {}
	if len(find_user1) == 0:
		reset_doc = {'email_' : email, 'code' : sha256_crypt.encrypt(reset_code), 'admin' : True, 'timestamp' : datetime.now()}
	else:
		reset_doc = {'email_' : email, 'code' : sha256_crypt.encrypt(reset_code), 'admin' : False, 'timestamp' : datetime.now()}
	creds.insert_one(reset_doc)

	payload = {'email' : email}
	result = urlencode(payload)
	email_user = result[result.index('=') + 1 : ]

	subject = "Reset Password"
	content = "Reset Code: " + reset_code + "\nGo to http://" + host + ":5000/reset_password/" + email_user + " to reset your password and type in the above code.\nPlease don't reply to this message."
	mail = smtplib.SMTP('smtp.gmail.com', 587)

	mail.ehlo()

	mail.starttls()

	mail.login('crime.forecast56@gmail.com', 'cyprus54#')

	msg = 'Subject: {}\n\n{}'.format(subject, content)
	mail.sendmail('crime.forecast56@gmail.com', email, msg)

	mail.close()
	flash('A reset code has been sent to your email address', 'success')
	return redirect(url_for('reset_password', email = email))

@app.route("/forgot", methods = ['GET', 'POST'])
def forgot():
	form = ForgotPassword()

	if request.method == 'POST':
		if form.validate_on_submit():

			client = MongoClient("mongodb+srv://test:test123%23@cluster0-l5ord.mongodb.net/test?retryWrites=true&w=majority")
			db1 = client.get_database('user_db')
			db2 = client.get_database('admin_db')

			u_creds = db1.user_creds
			a_creds = db2.admin_creds

			find_user1 = list(u_creds.find({'email' : form.email.data}))
			find_user2 = list(a_creds.find({'email' : form.email.data}))

			if len(find_user1) == 0 and len(find_user2) == 0:
				flash('Please enter the email associated to your account', 'danger')
			else:

				flash('A password reset code has been sent to your email address', 'success')

				reset_code = randomStringDigits(8)

				reset_doc = {}
				if len(find_user1) == 0:
					reset_doc = {'email_' : form.email.data, 'code' : sha256_crypt.encrypt(reset_code), 'admin' : True, 'timestamp' : datetime.now()}
				else:
					reset_doc = {'email_' : form.email.data, 'code' : sha256_crypt.encrypt(reset_code), 'admin' : False, 'timestamp' : datetime.now()}

				r_creds = client.get_database('reset_db').reset_creds
				r_creds.delete_many({'email_' : form.email.data})
				r_creds.insert_one(reset_doc)

				payload = {'email' : form.email.data}
				result = urlencode(payload)
				email_user = result[result.index('=') + 1 : ]

				subject = "Reset Password"
				content = "Reset Code: " + reset_code + "\nGo to http://" + host + ":5000/reset_password/ " + email_user + " to reset your password and type in the above code.\nPlease don't reply to this message."
				mail = smtplib.SMTP('smtp.gmail.com', 587)

				mail.ehlo()

				mail.starttls()

				mail.login('crime.forecast56@gmail.com', 'cyprus54#')

				msg = 'Subject: {}\n\n{}'.format(subject, content)
				mail.sendmail('crime.forecast56@gmail.com', form.email.data, msg)

				mail.close()

				return redirect(url_for('reset_password', email = form.email.data))

	return render_template('forgot.html', title = 'Forgot Password', form = form)

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
					session.permanent = True

					flash('Welcome ' + session['username'] + '!', 'success')
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

@app.route("/ad_login", methods = ['GET', 'POST'])
def ad_login():

	form = LoginForm()

	if request.method == "POST":
		if form.validate_on_submit():
			client = MongoClient("mongodb+srv://test:test123%23@cluster0-l5ord.mongodb.net/test?retryWrites=true&w=majority")
			db = client.get_database('admin_db')
			creds = db.admin_creds
			find_user = list(creds.find({'email':form.email.data}))

			if len(find_user) == 1:
				if sha256_crypt.verify(form.password.data, find_user[0]['passwd']):
					session['email'] = form.email.data
					session['username'] = find_user[0]['username']
					session['admin'] = 1
					session.permanent = True

					flash('Welcome ' + session['username'] + '!', 'success')
					#logged_in = True
					return redirect(url_for('ad_home'))
				else:
					flash('Please enter the correct email or password', 'danger')

			else:
				flash('Please enter the correct email or password', 'danger')

	else:

		if 'username' in session and 'email' in session:
			flash("You're already logged in", 'success')

			if 'admin' in session:
				return redirect(url_for('ad_home'))

			return redirect(url_for('home'))

	return render_template('admin_login.html', title = 'Admin Login', form = form)

@app.route("/register", methods = ['GET', 'POST'])
def register():
	#if logged_in:
		#flash('You are already logged in', 'success')
		#return redirect(url_for('home'))

	form = RegistrationForm()
	if request.method == "POST":
		if form.validate_on_submit():

			# print("I'm here")

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
				session.permanent = True

				flash(f'Account created for {form.username.data}!', 'success')
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

@app.route('/ad_register', methods = ['GET', 'POST'])
def ad_register():
	form = RegistrationForm()

	if request.method == 'POST':

		if form.validate_on_submit():

			client = MongoClient("mongodb+srv://test:test123%23@cluster0-l5ord.mongodb.net/test?retryWrites=true&w=majority")
			db = client.get_database('admin_db')
			creds = db.admin_creds
			dup_user = list(creds.find({'username' : form.username.data}))
			dup_email = list(creds.find({'email' : form.email.data}))

			if len(dup_user) == 0 and len(dup_email) == 0:
				enc_pass = sha256_crypt.encrypt(form.password.data)

				new_user = {'username' : form.username.data, 'email' : form.email.data, 'passwd' : enc_pass}
				creds.insert_one(new_user)

				session['email'] = form.email.data
				session['username'] = form.username.data
				session['admin'] = 1
				session.permanent = True

				flash(f'Account created for {form.username.data}!', 'success')
				return redirect(url_for('ad_home'))

			elif len(dup_user) == 0:
				flash(f'{form.email.data} is already in use', 'danger')

			else:
				flash(f'{form.username.data} is already in use', 'danger')

	else:

		if 'username' in session and 'email' in session:
			flash("You're already logged in", 'success')

			if 'admin' in session:
				return redirect(url_for('ad_home'))

			return redirect(url_for('home'))
	return render_template('admin_register.html', title = 'Admin Sign Up', form = form)


def randomStringDigits(stringLength = 6):

    """
    Generate a random string of letters and digits
    """

    lettersAndDigits = string.ascii_letters + string.digits
    return ''.join(random.choice(lettersAndDigits) for i in range(stringLength))

if __name__ == '__main__':
	#logged_in = False
	app.run(host = host, debug = True)
