import datetime
import json

from app import db

#for occupancy
class GSR_Info(db.Model):
	__tablename__ = 'gsr_info'

	id = db.Column(db.Integer, primary_key=True)
	status_timestamp = db.Column(db.DateTime, default=datetime.datetime.utcnow, onupdate=datetime.datetime.utcnow)
	faculty = db.Column(db.String(40), unique = False)
	gsr_id = db.Column(db.Integer, unique = False)
	gsr_no = db.Column(db.String(40), unique = False)
	Status = db.Column(db.String(40), unique = False)

	def __init__(self,gsr_id,gsr_no,status,faculty):
		self.gsr_id = gsr_id
		self.gsr_no = gsr_no
		self.Status = status
		self.faculty = faculty

	def serialize(self):
		return {
		"id":self.id,
		"timestamp": self.status_timestamp,
		"faculty": self.faculty,
		"gsr_id": self.gsr_id,
		"gsr_no": self.gsr_no,
		"status": self.Status,
		}

#show auto cancellation of booking due to inactivity
class Cancelled(db.Model):
	__tablename__ = 'c_info'

	id = db.Column(db.Integer, primary_key=True)
	status_timestamp = db.Column(db.DateTime, default=datetime.datetime.utcnow, onupdate=datetime.datetime.utcnow)
	faculty = db.Column(db.String(40), unique = False)
	gsr_id = db.Column(db.Integer, unique = False)
	gsr_no = db.Column(db.String(40), unique = False)

	def __init__(self,faculty,gsr_id,gsr_no):
		self.gsr_id = gsr_id
		self.gsr_no = gsr_no
		self.faculty = faculty

	def serialize(self):
		return {
		"id":self.id,
		"timestamp": self.status_timestamp,
		"faculty": self.faculty,
		"gsr_id": self.gsr_id,
		"gsr_no": self.gsr_no
		}
