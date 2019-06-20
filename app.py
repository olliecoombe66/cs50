import csv

from flask import Flask, jsonify, redirect, render_template, request, session
from flask_session import Session
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
		print(difficulty)

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

@app.route("/", methods=["GET"])
def get_index():
	return render_template("/difficulty.html")



