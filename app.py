# Step 01: import necessary libraries/modules
from flask import Flask, jsonify, request
from flask_sqlalchemy import SQLAlchemy
import os
# your code begins here 
# #  'postgresql://project_user:password@localhost:5432/project_a'
#  
# Step 02: initialize flask app here 
app = Flask(__name__)
app.debug = True

# Step 03: add database configurations here
app.config['SQLALCHEMY_DATABASE_URI'] = os.environ.get('DATABASE_URL') 
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db = SQLAlchemy(app)

# Step 04: import models
from models import GSR_Info, Cancelled

@app.route('/',methods = ['GET'])
def intro():
	return 'Analysis for ASK.GSR'

@app.route('/gsr_info/',methods = ['POST'])
def create_status():
	gsr_id = request.json['gsr_id']
	gsr_no = request.json['gsr_no']
	status = request.json['status']
	faculty = request.json['faculty']

	try:
		new_status = GSR_Info(gsr_id= gsr_id, gsr_no = gsr_no, status = status, faculty =faculty)
		db.session.add(new_status)
		db.session.commit()
		return jsonify('room status added!')

	except Exception as e:
		return str(e)

@app.route('/gsr_info/',methods =['GET'])
def check_gsr():
	GSR = GSR_Info.query.all()
	return jsonify([i.serialize() for i in GSR])


@app.route('/cancelled_info/',methods = ['POST'])
def create_cancelled():
	gsr_id = request.json['gsr_id']
	gsr_no = request.json['gsr_no']
	faculty = request.json['faculty']

	try:
		new_cancelled = Cancelled_Info(gsr_id = gsr_id, gsr_no = gsr_no, faculty = faculty)
		db.session.add(new_cancelled)
		db.session.commit()
		return jsonify('Cancelled info updated!')

	except Exception as e:
		return str(e)
