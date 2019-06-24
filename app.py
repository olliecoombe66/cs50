import csv

from flask import Flask, jsonify, redirect, render_template, request, session
from flask_session import Session
from werkzeug.security import check_password_hash, generate_password_hash
import sqlite3

# Configure application
app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'birds.db'
app.config.from_object(__name__)
app.config['SESSION_TYPE'] = 'filesystem'

Session(app)

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


@app.route("/difficulty", methods =["GET", "POST"])
def difficulty():
	if(request.method == "GET"):
		return render_template("/difficulty.html")

	if(request.method == "POST"):
		difficulty = request.form.get("difficulty")

		#connect to DB
		connection = sqlite3.connect('birds.db')

		#execute query
		cursor = connection.cursor()
		cursor.execute("SELECT DISTINCT english_cname,file_id, difficulty, option_a, option_b, option_c, question_id  FROM birdsong_metadata WHERE difficulty = ? GROUP BY english_cname", (difficulty))
		
		#get all responses
		rows = cursor.fetchall()

		#create dictionary for result (not used)
		result = []
		for row in rows:
			d = dict()
			d['name'] = row[0]
			d['file_id'] = row[1]
			d['difficulty'] = row[2]
			d['option_a'] = row[3]
			d['option_b'] = row[4]
			d['option_c'] = row[5]
			d['question_id'] = row[6]
			result.append(d)

		print(result)
	
		connection.commit()
		msg="Done"

		return render_template("/bird-test.html", bird_dictionary=result)

@app.route("/register", methods=["GET", "POST"])
def register():

	if request.method == "GET":
		return render_template("register.html")

	elif request.method=="POST":
		username = request.form.get("username")
		password = request.form.get("password")
		confirm_password = request.form.get("confirm_password")
		hash = generate_password_hash(password)

		connection = sqlite3.connect('birds.db')
		cursor = connection.cursor()
		cursor.execute("INSERT INTO users (`user_name`, `password`,`level`) VALUES (?,?,?)", (username,password,1,))
		connection.commit()


		return render_template("difficulty.html")


"""
		if username == None:
        	return(0)
        elif password != confirm_password:
        	return0
        elif not new_user_id:
            return 0
        else:
            session["user_id"] = new_user_id
"""

@app.route("/login", methods=["GET"])
def login():
	# Forget any user_id
    session.clear()

    # User reached route via POST (as by submitting a form via POST)
    if request.method == "POST":

        # Ensure username was submitted
        

        # Ensure password was submitted

        # Query database for username
        rows = db.execute("SELECT * FROM users WHERE username = :username",
                          username=request.form.get("username"))

        # Ensure username exists and password is correct
        if len(rows) != 1 or not check_password_hash(rows[0]["hash"], request.form.get("password")):
            return apology("invalid username and/or password", 403)

        # Remember which user has logged in
        session["user_id"] = rows[0]["id"]

        # Redirect user to home page
        return render_template("/difficulty.html")

    # User reached route via GET (as by clicking a link or via redirect)
    else:
        return render_template("login.html")

@app.route("/", methods=["GET"])
def get_index():
	
	return render_template("index.html")



