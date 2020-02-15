from flask import Flask, render_template, redirect, url_for, flash
from form import RegistrationForm, LoginForm

app = Flask(__name__)
app.config['SECRET_KEY'] = '0f728c6b5c9f6e02690f9496da4818ae'

@app.route("/")
@app.route("/home")
def home():
	return render_template('index.html')

@app.route("/about")
def about():
	return render_template('about.html', title = 'About')

@app.route("/map")
def map():
	return render_template('map.html', title = 'Map')

@app.route("/forgot")
def forgot():
	return render_template('forgot.html')

@app.route("/login", methods = ['GET', 'POST'])
def login():
	form = LoginForm()
	if form.validate_on_submit():
		if form.email.data == 'admin@gmail.com' and form.password.data == '123456':
			flash('You have been logged in!', 'success')
			return redirect(url_for('home'))
		else:
			flash('Please enter the correct email or password', 'danger')

	return render_template('login.html', title = 'Login', form = form)

@app.route("/register", methods = ['GET', 'POST'])
def register():
	form = RegistrationForm()
	if form.validate_on_submit():
		flash(f'Account created for {form.username.data}!', 'success')
		return redirect(url_for('home'))
	return render_template('register.html', title = 'Register', form = form)

if __name__ == '__main__':
	app.run(debug = True)