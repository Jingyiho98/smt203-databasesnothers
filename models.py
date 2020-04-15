import datetime
import json

from app import db

booking_and_slot = db.Table('booking_slot', 
	db.Column('booking_id', db.Integer, db.ForeignKey('booking.id'), primary_key=True),
	db.Column('slot_id', db.Integer, db.ForeignKey('slot.id'), primary_key=True))


class Student(db.Model):
	__tablename__ = 'student'

	id = db.Column(db.Integer,primary_key=True,nullable=False)
	email = db.Column(db.String(80),unique=True,nullable=False)
	name = db.Column(db.String(80),unique = False,nullable=False)
	telegram_chat_id = db.Column(db.Integer, unique=True,nullable = False)
	credits = db.Column(db.Integer, unique=False, nullable=False)
	no_of_penalty = db.Column(db.Integer, unique=False, nullable=False)
	status = db.Column(db.String(30), unique=False, nullable=False)

	bookings = db.relationship('Booking', back_populates='studentx', uselist=True, cascade = 'all, delete-orphan')


	def __init__(self, email,name, telegram_chat_id):
		self.email = email
		self.name = name
		self.telegram_chat_id = telegram_chat_id
		self.credits = 80
		self.no_of_penalty = 0
		self.status = 'Active' #if banned, is 'Inactive'
		self.bookings = []

	def serialize(self):
		return {
			'email': self.email,
			'name': self.name,
			'credits': self.credits,
			'no_of_penalty': self.no_of_penalty, 
			'status': self.status,
			'bookings':[{"bookingref": b.bookingref, "faculty": b.faculty, "date": b.date, "slot(s)": [s.id for s in b.slotx] } for b in self.bookings]
		}

class GSR(db.Model):
	__tablename__ = 'gsr'

	id = db.Column(db.Integer, primary_key=True, nullable=False)
	GSR_No = db.Column(db.String(10),unique=False,nullable=False)
	faculty = db.Column(db.String(40), unique=False,nullable = False)
	level = db.Column(db.Integer, unique=False, nullable=False)

	booking = db.relationship('Booking', back_populates='gsrx', uselist= True)
	sensorx = db.relationship('Sensor', back_populates='gsr2')


	def __init__(self,GSR_No, faculty, level):
		self.GSR_No = GSR_No
		self.faculty = faculty
		self.level = level


	def serialize(self):
		return {
			'GSR_No': self.GSR_No,
			'faculty': self.faculty,
			'level': self.level, 
		}


class Booking(db.Model):
	__tablename__ = 'booking'

	# bookingref = db.Column(db.String(40),primary_key=True,nullable=False) #OLD
	id = db.Column(db.Integer,primary_key=True,nullable=False)
	bookingref = db.Column(db.Integer,unique=True,nullable=False) #NEW
	date = db.Column(db.String(40), unique=False,nullable = False)
	bookingstatus = db.Column(db.String(40), unique=False,nullable = False)
	student_id = db.Column(db.Integer, db.ForeignKey('student.id') ,nullable = False)
	gsr_id = db.Column(db.Integer, db.ForeignKey('gsr.id') ,nullable = False)
	faculty = db.Column(db.String(40), unique=False, nullable = False)

	studentx = db.relationship('Student', back_populates='bookings')

	gsrx = db.relationship('GSR', back_populates='booking')

	slotx  = db.relationship('Slot', secondary=booking_and_slot, back_populates='bookingx', cascade='all', lazy=True) #NEW

	def __init__(self, booking_ref ,faculty,date,student_id,gsr,slot):
		self.bookingref = booking_ref
		self.date = date
		self.faculty = faculty
		self.bookingstatus = "Confirmed"
		self.student_id = student_id
		self.gsr_id = gsr
		self.slotx = slot


	def serialize(self):
		return {
	 #ADD R/s
		"bookingref":self.bookingref,
		"faculty":self.faculty,
		"gsr": self.gsr_id,
		"date":self.date,
		"slots": [s.id for s in self.slotx],
		"booking_status": self.bookingstatus
		}


class Sensor(db.Model):
	__tablename__ = 'sensor'

	id = db.Column(db.Integer, primary_key=True,unique = True, nullable=False)
	room_status = db.Column(db.String(20), unique = False, nullable= False)
	gsr = db.Column(db.Integer,db.ForeignKey('gsr.id'), nullable = False)

	gsr2 = db.relationship('GSR', back_populates='sensorx')

	def __init__(self,sensorid,gsr):
		self.id = sensorid
		self.room_status = "False"
		self.gsr = gsr

	def serialize(self):
		return{
		"sensorid": self.id,
		"gsr":self.gsr,
		"room_status": self.room_status
		}

class Slot(db.Model):
	__tablename__ = 'slot'

	id = db.Column(db.Integer, primary_key=True,unique = True, nullable=False)
	start_time = db.Column(db.Integer, unique = False, nullable= False)
	end_time = db.Column(db.Integer, unique = False, nullable= False)

	bookingx = db.relationship('Booking', secondary=booking_and_slot, back_populates='slotx') #NEW

	def __init__(self,slot_id,start_time,end_time):
		self.id = slot_id
		self.start_time = start_time
		self.end_time = end_time

	def serialize(self):
		return{
		"slotid": self.id,
		"start_time":self.start_time,
		"end_time": self.end_time
		}

