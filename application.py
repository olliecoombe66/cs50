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
		cursor.execute("SELECT file_id, english_cname,difficulty FROM birdsong_metadata WHERE difficulty = %s)", (difficulty))
		
		#get all responses
		rows = cursor.fetchall()
		connection.commit()
		msg="Done"

		return render_template("/birds.html", bird_dictionary=rows)

@app.route("/", methods=["GET"])
def get_index():
	return render_template("/difficulty.html")


@app.route("/birds", methods=["POST", "GET"])
def birds():

	return render_template("/birds.html", rows=bird_dictionary)
		#, bird_dictionary=rows"""


