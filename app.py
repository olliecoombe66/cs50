import csv


from flask import Flask, jsonify, redirect, render_template, request, session, flash, url_for
from flask_session import Session
from werkzeug.security import check_password_hash, generate_password_hash
from flask_sqlalchemy import SQLAlchemy
import sqlite3
import os
from sqlalchemy import create_engine
from sqlalchemy import Table, Column, Integer, String, MetaData, ForeignKey, func
from sqlalchemy.sql import select, distinct

# Configure application
app = Flask(__name__)
app.secret_key = 'sdflslvsdmllsdmlcsc'



# Use SQLAlchemy
engine = create_engine('sqlite:///birds.db', echo=False)
conn = engine.connect()
metadata = MetaData()
SQLITE = 'sqlite'

users = Table('users', metadata,
	Column('id', Integer),
	Column('user_name', String),
	Column('password', String),
	Column('level', Integer),
	)

birds = Table('birdsong_metadata_2', metadata,
	Column('file_id', String),
	Column('genus', String),
	Column('species', String),
	Column('english_cname', String),
	Column('Difficulty', Integer),
	Column('option_a', String),
	Column('option_b', String),
	Column('option_c', String),
	Column('option_d', String),
	Column('question_id', String),
	)

metadata.create_all(engine)

class MyDatabase:
    # http://docs.sqlalchemy.org/en/latest/core/engines.html
    DB_ENGINE = {
        SQLITE: 'sqlite:///birds.db'
    }

# Table Names
USERS = 'users'
ADDRESSES = 'addresses'

#functions
def check_username(x):
	#check if username exists
	with engine.connect() as conn:
		result = conn.execute(select([users.c.user_name]).where(users.c.user_name == x))
		user_name_count=list(result.fetchall())
	return(user_name_count)

#gets the questions for the user's level. just requires user level
def bird_results(z):
	with engine.connect() as conn:

		y = conn.execute(select([(distinct(birds.c.english_cname)), birds.c.Difficulty, birds.c.option_a, birds.c.option_b, birds.c.option_c, birds.c.option_d, birds.c.question_id, birds.c.file_id])
			.where(birds.c.Difficulty == z)
			.group_by(birds.c.english_cname))

		result = []
		for row in y:
			d = dict()
			d['name'] = row[0]
			d['difficulty'] = row[1]
			d['option_a'] = row[2]
			d['option_b'] = row[3]
			d['option_c'] = row[4]
			d['option_d'] = row[5]
			d['question_id'] = row[6]
			d['file_id'] = row[7]
			result.append(d)

		return result

@app.route('/set/')
def set():
    session['key'] = 'value'
    return 'ok'

@app.route('/get/')
def get():
    return session.get('key', 'not set')

# Reload templates when they are changed
app.config["TEMPLATES_AUTO_RELOAD"] = True

@app.after_request
def after_request(response): 
    """Disable caching"""
    response.headers["Cache-Control"] = "no-cache, no-store, must-revalidate"
    response.headers["Expires"] = 0
    response.headers["Pragma"] = "no-cache"
    return response

@app.route("/bird-test", methods =["GET", "POST"])
def bird_test():
	if(request.method == "GET"):

		level = session.get("level") 
		result = bird_results(level)

		return render_template("/bird-test.html", bird_dictionary=result, level=level)

	elif(request.method == "POST"):

		level = session.get("level") 
		level +=1

		username = session.get("username")
		result = bird_results(level)

		connection = sqlite3.connect('birds.db')
		cursor = connection.cursor()
		cursor.execute("UPDATE users SET level = ? WHERE user_name = ?", (level,username,))
		session['level']=level
		connection.commit()

		return render_template("/bird-test.html", bird_dictionary=result, level=level)

@app.route("/register", methods=["GET", "POST"])
def register():

	if request.method == "GET":
		return render_template("register.html")

	elif request.method=="POST":
		username = request.form.get("username")
		password = request.form.get("password")
		confirm_password = request.form.get("confirm_password")
		hash = generate_password_hash(password, method='pbkdf2:sha256', salt_length=8)

		if username == '':
			error = 'Username cannot be blank'
			return render_template("register.html", error=error)

		elif password == '':
			error = 'Password may not be blank'
			return render_template("register.html", error=error)

		elif password != confirm_password:
			error = 'Passwords do not match'
			return render_template("register.html", error=error)

		elif len(check_username(username)) > 0:
			error = 'Username already taken'
			return render_template("register.html", error=error)

		else:
			connection = sqlite3.connect('birds.db')
			cursor = connection.cursor()
			cursor.execute("INSERT INTO users (`user_name`, `password`,`level`) VALUES (?,?,?)", (username,hash,1,))
			connection.commit()
			session['username']=request.form['username']
			session['level'] = 1
			return redirect(url_for("bird_test"))

@app.route("/login", methods=["GET", "POST"])
def login():
	# Forget any user_id
    #session.clear()
	if(request.method == "GET"):

		return render_template("login.html")

    # User reached route via POST (as by submitting a form via POST)
	elif(request.method == "POST"):
		username = request.form.get("username")
		password = request.form.get("password")

		# Ensure username was submitted
		if(username == ''):
			error = 'Username cannot be blank'
			return render_template("login.html", error=error)

		# Ensure password was submitted
		elif(password == ''):
			error = 'Password may not be blank'
			return render_template("login.html", error=error)

		elif len(check_username(username)) == 0:
			error = 'Username does not exist'
			return render_template("login.html", error=error)

		else:
			#get password and extract it from SQL response
			connection = sqlite3.connect('birds.db')
			cursor = connection.cursor()
			cursor.execute("SELECT * FROM users WHERE user_name = ?", (username,))			
			user_details=list(cursor.fetchall())
			result = []
			for row in user_details:
				d = dict()
				d['hash'] = row[1]
				d['level'] = row[2]
				result.append(d)
		
			password_hash = (result[0]['hash'])

			if (check_password_hash(password_hash, password)) == True:
				session['username']=request.form['username']
				session['level']=result[0]['level']

				return redirect(url_for("bird_test"))
				
			else: 
				error = 'Incorrect password'
				return render_template("login.html", error=error)


@app.route("/", methods=["GET"])
def get_index():
	return render_template("index.html")

if __name__ == '__main__':
	app.run(host="0.0.0.0",debug=True)

