# Step 01: import necessary libraries/modules
from flask import Flask, jsonify, request
from flask_sqlalchemy import SQLAlchemy
import os
import requests
from datetime import datetime
import json
# your code begins here 'postgresql://project_user:password@localhost:5432/project_db'
# os.environ.get('DATABASE_URL')
# Step 02: initialize flask app here 
app = Flask(__name__)
app.debug = True

# Step 03: add database configurations here
app.config['SQLALCHEMY_DATABASE_URI'] = os.environ.get('DATABASE_URL')
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db = SQLAlchemy(app)

# Step 04: import models
from models import Student, GSR, Slot, Booking, Sensor
 #NEW havent commit
api_token = #change this to api token"

@app.route('/', methods=['GET']) 
def hello():
	return 'WELCOME TO ASK.GSR'

@app.route('/students/', methods=['POST']) 
def create_student_details():
	email = request.json['email']
	chat_id = request.json['tele_chat_id']
	name = request.json['name']

	try:
		new_student = Student(email = email, name = name, telegram_chat_id = chat_id)
		db.session.add(new_student)
		db.session.commit()
		return jsonify('"Response Status": "Student {} Successfully Created"'.format(email))

	except Exception as e:
		return(str(e))

@app.route('/gsr/', methods=['POST'])
def create_gsr():
	gsr_no = request.json['GSR_No']
	faculty = request.json['Faculty']
	level = request.json['Level']
	try:
		gsr = GSR.query.filter(GSR.faculty == faculty, GSR.GSR_No == gsr_no).first()
		if gsr == None:
			new_gsr = GSR(GSR_No= gsr_no, faculty = faculty, level= level)
			db.session.add(new_gsr)
			db.session.commit()
			return jsonify('"Response Status": "GSR {} Successfully Created"'.format(gsr_no))
		else:
			return ("GSR already exist!")

	except Exception as e:
		return(str(e ))


@app.route('/booking/', methods=['POST'])
#create booking and deduct credits if successfully 
def create_booking():
	#{"faculty":"SIS","date":"2020-04-15","gsr":"2-4","slot":[11,12],"chatid":281997556}
	chat_id = request.json['chat_id']
	faculty = request.json['faculty']
	gsr = request.json['gsr_no'] #string 
	slot = request.json['slots']
	date = request.json['date']
	student = Student.query.filter_by(telegram_chat_id=chat_id).first()
	slots_list = []
	# gsr = gsr.strip()
	new_date = datetime.strptime(date, '%Y-%m-%d').date()
	now = datetime.now()
	this = now.strftime("%Y-%m-%d")
	another = now.strftime("%Y%m%d")
	current_date = datetime.strptime(str(this), '%Y-%m-%d').date()
	for_bkref = int(now.strftime("%Y%m%d"))
	current_time = int(now.strftime("%H%M"))
	#include deduct credit when sucessfully booked. (update-PUT)
	#only book a max of 3 hours for each booking day

	if sorted(slot)==list(range(min(slot), max(slot)+1)):

		if new_date >= current_date:
			#######################
			a = Booking.query.filter_by(date=date).filter(Booking.gsrx.has(faculty=faculty)).filter_by(bookingstatus="Confirmed")

			book_dict = {}
			for i in a:                                         # put all the booked slots of a gsr tgt
				gsr_list = []                                   # format : {gsr 1: [1, 2, 3,], gsr 2: [1, 5, 8]}
				gsr_id = i.gsr_id
				gsr_name = GSR.query.filter_by(id=gsr_id).first().GSR_No

				slot_name = i.slotx
				
				if gsr_id in book_dict:
					gsr_list=book_dict.get(gsr_name)
					gsr_list= gsr_list + slot_name
					book_dict.update({gsr_name:gsr_list})
				else:
					gsr_list = slot_name
					book_dict.update({gsr_name:gsr_list})

			already_booked =[]
			for k, v in book_dict.items():
				if k == gsr:
					for i in v:
						if i.id in slot:
							already_booked.append(i.id)
							print (already_booked)
							tosend = "Some slots have already been booked"

			if already_booked != []:
				tosend = "Slots "+ str(already_booked) + " have already been booked" 
				return jsonify(tosend)

			else:
				for i in slot:
					something = Slot.query.filter_by(id = i).first()
					if something != None:
						slots_list.append(something)
				if len([i for i in slots_list])>3: #check 
					tosend = "You can only book a room for a maximum of 3 hours per day"
					print (tosend)
				else:
					booking_made = Booking.query.filter_by(student_id=student.id).filter_by(date=date).filter_by(bookingstatus= "Confirmed")
					check_bookings = [i.slotx for i in booking_made]

					count = 0
					for i in check_bookings:			#check the number of slots booked on the date
						count += len(i)

					if count <3:						#if number of slots is less than 3, booking can still be made
						avail_slots_tobook = 3 - count 	#number of slots still available to book after counting all bookings on the date

						if len([i for i in slots_list]) > avail_slots_tobook:
							tosend = "The current booking you are attempting to make have exceeded the maximum 3 hours of booking GSR per day\n You are left with " + str(avail_slots_tobook) + " slot(s) booking"
							print (tosend)
						else:
							create_gsr = GSR.query.filter_by(faculty=faculty).filter_by(GSR_No=gsr).first()
							bookingref = int(student.id)+int(create_gsr.id)+int(for_bkref)+int(current_time)
							print(bookingref)


							if new_date==current_date:
								max_slot = max([i.id for i in slots_list])  #ERROR IS HERE!
								print ('test',max_slot)
								max_query = Slot.query.filter_by(id=max_slot).first()
								if max_query.end_time < current_time:
									return jsonify("Booking not allowed. Slot is past the current timing")
								else:
									try:
										hello = Booking(booking_ref = bookingref, date = date, student_id= student.id, gsr=create_gsr.id,slot = slots_list, faculty=faculty)
										db.session.add(hello)
										db.session.commit()
										credits_return = len([i.id for i in slots_list])
										student.credits = student.credits-credits_return
										db.session.commit()
										photo_url = 'https://www.sciencealert.com/images/2020-03/processed/010-pomeranian_1024.jpg'
										# chat_id = 280422800
										base_url = 'https://api.telegram.org/bot{}/'.format(api_token)
										msg_text = 'Your bookingref#{} has been created'.format(bookingref)
				#send slots id and start time end time here!!!
										sendPhoto_url = base_url + 'sendPhoto'
										params2 = {'chat_id': chat_id, 'photo': photo_url}
										sendMsg_url = base_url + 'sendMessage'
										params1 = {'chat_id': chat_id, 'text': msg_text}
										r2 = requests.post(sendMsg_url, params = params1)
										send_dog = requests.post(sendPhoto_url, params = params2)
										return jsonify('"Response Status": "Bookingref Successfully Created"')

									except Exception as e:
										return(str(e))
								
							else:
								try:
									hello = Booking(booking_ref = bookingref, date = date, student_id= student.id, gsr=create_gsr.id,slot = slots_list, faculty=faculty)
									db.session.add(hello)
									db.session.commit()
									credits_return = len([i.id for i in slots_list])
									student.credits = student.credits-credits_return
									db.session.commit()
									msg_text = 'Your booking #{} has been created.'.format(bookingref)
									# chat_id = 280422800
									photo_url = 'https://www.sciencealert.com/images/2020-03/processed/010-pomeranian_1024.jpg'
									base_url = 'https://api.telegram.org/bot{}/'.format(api_token)
									sendPhoto_url = base_url + 'sendPhoto'
									sendMsg_url = base_url + 'sendMessage'
									params = {'chat_id': chat_id, 'text': msg_text}
									params2 = {'chat_id': chat_id, 'photo': photo_url}
									r2 = requests.post(sendMsg_url, params = params)
									send_dog = requests.post(sendPhoto_url, params = params2)

									return jsonify('"Response Status": "Bookingref Successfully Created"')

								except Exception as e:
									return(str(e))
					else:
						tosend = "You have exceeded the number of booking you can make for this date"
						print (tosend)
		else:
			tosend = "Please enter a valid date"
			return (tosend)
	else:
		tosend = "Please select the slots with consecutive numbers"
	#BEAUTIFUL DO TELEGRAM REQUEST HERE
	
	
	msg_text = tosend
	# chat_id = 280422800
	base_url = 'https://api.telegram.org/bot{}/'.format(api_token)
	sendMsg_url = base_url + 'sendMessage'
	params = {'chat_id': chat_id, 'text': msg_text}
	r2 = requests.post(sendMsg_url, params = params)




@app.route('/students/', methods=['GET'])
def get_students():
	students = Student.query.all()

	if 'function' in request.args:
		chat_id = int(request.args.get('chat_id'))
		function = str(request.args.get('function'))

		if function == 'checkexist':
			exist = Student.query.filter_by(telegram_chat_id = chat_id).first()
			if exist is None:
				return "Not from SMU" #tentative #not from SMU
			elif exist.status == "Inactive": 
				return "Banned" #banned
			elif exist != None:
				return "Available" #tentative #from SMU


		if function == 'checkuser':

			exist = Student.query.filter_by(telegram_chat_id = chat_id).first()
			if exist is None: #not from smu
				tosend = "Sorry, you're not from SMU and have no rights to access"
				base_url = 'https://api.telegram.org/bot{}/'.format(api_token)
				sendMsg_url = base_url + 'sendMessage'
				params = {'chat_id': chat_id, 'text': tosend}
				r2 = requests.post(sendMsg_url, params = params)

				return ":("  #tentative #not from SMU

			else:
				name = exist.name
				email = exist.email
				credits = exist.credits
				penalty = exist.no_of_penalty
				status = exist.status
				

				current_booking = Student.query.filter_by(telegram_chat_id = chat_id).filter(Student.bookings.any(bookingstatus = "Confirmed")).first()
				print(current_booking)
				string = ""
				if exist.bookings != None:
					for b in exist.bookings:
						bookingref = b.bookingref
						faculty = b.faculty
						date = b.date
						gsr_id = b.gsr_id
						gsr_no = GSR.query.filter_by(id = gsr_id).first().GSR_No
						if b.bookingstatus == "Confirmed":
							slots = [s.id for s in b.slotx] 
							new_string = "Bookingref: " +  str(bookingref) + "\n" + "Faculty: " + str(faculty) + "\n" + "GSR_No: " +str(gsr_no) +"\n" + "Date: " + str(date) + "\n" + "Slot(s): " + str(slots) + "\n" + "\n"
							string = string + new_string
				else:
					string = "\n" + "---No bookings has been made---"

				# booking = [{"bookingref": b.bookingref, "faculty": b.faculty, "date": b.date, "slot(s)": [s.id for s in b.slotx] } for b in exist.bookings]

				tosend = "User Details: " + "\n" + "\n" + "Name: " + str(name) + "\n" +  "Email: " + str(email) + "\n" + "Credits: " + str(credits) + "\n" +  "Penalty: " + str(penalty) + "\n" + "Status: " + str(status) + "\n" + "\n" + "Current Bookings: " + "\n" + string
				base_url = 'https://api.telegram.org/bot{}/'.format(api_token)
				sendMsg_url = base_url + 'sendMessage'
				params = {'chat_id': chat_id, 'text': tosend}
				r2 = requests.post(sendMsg_url, params = params)
				return ":)" #tentative #from SMU give

	return jsonify([s.serialize() for s in students])


# @app.route('/', methods=['GET'])
# def hello():
#   test = Student.query.all()
#   return jsonify([t.serialize() for t in test])

@app.route('/slot/', methods=['POST'])
def create_slot():
	slot_id = request.json['slot_id']
	starttime = request.json['starttime']
	endtime = request.json['endtime']

	try:
		new_slot = Slot(slot_id = slot_id, start_time = starttime, end_time = endtime)
		db.session.add(new_slot)
		db.session.commit()
		return jsonify('"Response Status": "slot {} Successfully Created"'.format(slot_id))

	except Exception as e:
		print(e)
		return(str(e ))

@app.route('/sensor/', methods=['POST'])
def create_sensor():
	sensorid = request.json['sensorid']
	gsr = request.json['gsr']

	try:
		new_sensor = Sensor(sensorid= sensorid, gsr = gsr)
		db.session.add(new_sensor)
		db.session.commit()
		return jsonify('"Response Status": "Sensor {} Successfully Created"'.format(sensorid))

	except Exception as e:
		return(str(e ))

@app.route('/sensor/', methods=['PUT']) 
def update_status():

	sensor_to_update = request.json['sensorid']
	status = request.json['status']
	to_update = Sensor.query.filter_by(id = sensor_to_update).first()
	gsr_id = Sensor.query.filter_by(id = sensor_to_update).first().id
	gsr_no = GSR.query.filter_by(id=gsr_id).first().GSR_No
	faculty = GSR.query.filter_by(id=gsr_id).first().faculty
	url = 'https://smt203-analysis.herokuapp.com/gsr_info/'
	json = {'gsr_id':gsr_id, 'gsr_no': gsr_no,'status': status,'faculty':faculty}
	r = requests.post(url, json = json)
	
	print('help1')

	if to_update != None:
		to_update.room_status = status
		db.session.commit()

	if status == "False":
		print('help2')
		slot = Slot.query.all()
		print(slot)
		time_now = int(datetime.now().strftime("%H%M"))
		date_now = datetime.now().strftime("%Y-%m-%d")
		print(time_now)
		print(date_now)
		print(slot)
		something  = [i.serialize() for i in slot]
		current_slot = ""
		print(something)
		try:
			for i in something:
				if time_now >= i["start_time"] and time_now <= i["end_time"]:
					current_slot = i.get("slotid")

			print(current_slot)
			print('hello')
			this_booking_check = Booking.query.filter_by(gsr_id = gsr_id).filter_by(date = date_now).all()
			print(':/')
			if this_booking_check != None:
				this_booking = Booking.query.filter_by(gsr_id = gsr_id).filter_by(date = date_now).filter_by(bookingstatus = "Confirmed").filter(Booking.slotx.any(id = current_slot)).first()
				print('check2')
				print(date_now)
				print(type(this_booking))
				
				if this_booking != None:
					print(this_booking)
					this_booking.bookingstatus = "Cancelled" 
					db.session.commit()
					print('check3')
					#update 2nd db 2nd table
					url2 = 'https://smt203-analysis.herokuapp.com/cancelled_info/'
					json = {'gsr_id': gsr_id, 'gsr_no': gsr_no, 'faculty':faculty}
					r = requests.post(url2, json = json)
					print('passed')

					#send to user cancelled message
					print('here?')
					msg_text = "Sorry, your booking #{} have been cancelled due to inactivity".format(this_booking.bookingref)
					this_student_id = Booking.query.filter_by(gsr_id = gsr_id).filter_by(date = date_now).filter(Booking.slotx.any(id = current_slot)).first().student_id
					chat_id = Student.query.filter_by(id = this_student_id).first().telegram_chat_id
					base_url = 'https://api.telegram.org/bot{}/'.format(api_token)
					sendMsg_url = base_url + 'sendMessage'
					params = {'chat_id': chat_id, 'text': msg_text}
					r2 = requests.post(sendMsg_url, params = params)
					print('here?2')

					#send sad dog
					photo_url = 'https://cff2.earth.com/uploads/2019/08/23135930/For-humans-a-whimpering-puppy-sounds-just-as-sad-as-a-crying-baby-.jpg'
					sendPhoto_url = base_url + 'sendPhoto'
					params2 = {'chat_id': chat_id, 'photo': photo_url}
					send_dog = requests.post(sendPhoto_url, params = params2)
					print('did this run>?')

					##### PLEASE UPDATE PENALTY HERE
					this_student = Student.query.filter_by(id = this_student_id).first()
					this_student.no_of_penalty = this_student.no_of_penalty + 1
					db.session.commit()
					if this_student.no_of_penalty >= 3:
						this_student.status = "Inactive"
						db.session.commit()

					return ":)"

		except Exception as e:
			return str(e)

# fill in the respective URLs here
# you should make use of the base_url variable 

	return jsonify(to_update.serialize())


	##NEW DE HAVENT COMMIT

@app.route('/availablegsr/', methods=['GET'])           # Hi, can read the comments at this tabbed column. 
def get_availbookings():                                # The rest can ignore. heh thanks 

	if 'function' in request.args:
		function = request.args.get('function')
		#CG GIVE THIS{“chat_id”:439595, “faculty”: “SIS”, “date”: “YYYY-MM-DD”, “function”: “checkavail”}
		date_req = request.args.get('date')
		faculty = request.args.get('faculty')
		chat_id = request.args.get('chat_id')
		date_now = datetime.now().strftime("%Y-%m-%d")
		time_now = int(datetime.now().strftime("%H%M"))
		print(time_now)

		print(date_req)
		print(date_now)

		# return format : {gsr 1: [1, 2, 3,], gsr 2: [1, 5, 8]}
		all_booked_slot = Booking.query.filter_by(date=date_req).filter(Booking.gsrx.has(faculty=faculty)).filter_by(bookingstatus="Confirmed")
		gsr_query = GSR.query.all()
		slot_query = Slot.query.all()

		avail_slots = {}
		check_gsr = [book.id for book in all_booked_slot]
		if len(check_gsr) == 0:
			if date_now == date_req:
				slot_list = [i.id for i in slot_query if i.start_time>= time_now]
			else:
				slot_list = [i.id for i in slot_query]
			for i in gsr_query:
				avail_slots.update({'GSR '+ i.GSR_No: slot_list})
			avail_list = [(k, v) for k, v in avail_slots.items()] 
			# avail_list = sorted(avail_slots.items())
			print (avail_slots)
			print('test')
			print(avail_list)
		else:
			booked_slot = {}
			for i in all_booked_slot:
				gsr_list = []
				gsr_id = i.gsr_id #get gsr_id from booking object 
				gsr_no = GSR.query.filter_by(id=gsr_id).first().GSR_No #get gsr_no from unique gsr_id

				slot_name = i.slotx

				if gsr_id not in booked_slot:
					gsr_list = slot_name
					booked_slot.update({gsr_no:gsr_list}) #add a new {'GSR 2-4': [1]} into dict

				else:
					gsr_list=booked_slot.get(gsr_no)
					gsr_list= gsr_list + slot_name #add new slots into existing gsr_no(key)
					booked_slot.update({gsr_no:gsr_list}) #update dict with new slots
			print ('a')
			print (booked_slot)
			all_slot_list = list(set(Slot.query.all()))

			

			for gsr_no, slots in booked_slot.items():               # get all the slots that are available
				avail_list = []                                 # format {gsr_id: [slot_id]}
				slotx =list(slots)
				print(slots)
				print('hi')
				for slot in all_slot_list: 
					if slot not in slots: #if not in slots, means it is available
						id = slot.id
						if date_req==date_now:
							if slot.start_time >= time_now:
								avail_list.append(id)
							else:
								continue
						else:
							avail_list.append(id)

				print (avail_list)
				new_avail = sorted(avail_list)
				avail_slots.update({'GSR '+ gsr_no: new_avail})
				print(new_avail)
			# print (avail_list)
			print(avail_slots)
			print('ni')
			
			

			for i in gsr_query:
				avail_list = []
				if str('GSR ' + i.GSR_No) not in avail_slots:
					if date_req == date_now:
						for slot in slot_query:
							if slot.start_time >= time_now:
								avail_list.append(slot.id)
					else:
						avail_list=[s.id for s in slot_query]
				else:
					continue
				avail_slots.update({'GSR '+ i.GSR_No: avail_list})
			avail_list = sorted(avail_slots.items())

			# avail_slots = {}
			for i in avail_list:
				avail_slots.update({i[0]:i[1]})

			print(avail_list)

		if function == "checkavail":
			tosend_avail = ""
			for i in avail_list:
				gsr = str(i[0])
				slot = str(i[1])
				new_string = gsr + " : " + slot + "\n" + "\n"
				tosend_avail = tosend_avail + new_string
			
			base_url = 'https://api.telegram.org/bot{}/'.format(api_token)
			url_get_slots_info = 'https://smt203-g7.herokuapp.com/slot/'
			a = requests.get(url_get_slots_info)
			slot_info = ""
			x = a.text
			test = json.loads(x)
			type(x)

			for k,v in test.items():
				slot_info = slot_info + "{0:<9} {1}".format(k,v) + "\n" + "\n"

			print(slot_info)
			print(type(slot_info))
			print('slotinfo')
			sendMsg_url = base_url + 'sendMessage'
				#send slots id and start time end time here!!!
			# sendPhoto_url = base_url + 'sendPhoto'
			# photo_url = 'https://drive.google.com/open?id=1UYf4R9WK4IA5Dna6eeOfTXcowp4rI1by'
			text = "```" + "\n"  +"{0:<9} {1}".format("Slot No.","Timing")+ "\n" +slot_info + "\n" + "```"
				#send available slot to 
			tosend =  "GSR_No: [Slots Available]"  + "\n"+ "\n" + tosend_avail

			params2 = {'chat_id': chat_id, 'text': text, 'parse_mode': 'Markdown'}
			send_slotinfo = requests.post(sendMsg_url, params = params2)

			params = {'chat_id': chat_id, 'text': tosend }
			send_to_user = requests.post(sendMsg_url, params = params)



			return ':)'

		#CHECK FOR BOOKING
		if function == "booking":
			return jsonify(avail_slots)

@app.route('/slot/', methods=['GET'])
def get_slot():
	all_slots = Slot.query.all()
	dictionary = {}
	for slot in all_slots:
		info = str(slot.start_time) + " to " + str(slot.end_time)
		dictionary.update({slot.id:info})


		# print (dictionary)
	return jsonify(dictionary)

@app.route('/currentbookings/', methods=['GET'])
def current_bookings():
	#include the date

	now = datetime.now()
	current_date = now.strftime("%Y-%m-%d")
	current_time = int(now.strftime("%H%M"))
	try: 
		chatid = request.args.get('chatid')
		# email = request.args.get('email')
		student = Student.query.filter_by(telegram_chat_id=chatid).first()
		# student = Student.query.filter_by(email=email).first()
		bookings_current = Booking.query.filter_by(student_id=student.id).filter(Booking.date==current_date).filter_by(bookingstatus="Confirmed")
		bookings_future = Booking.query.filter_by(student_id=student.id).filter(Booking.date>current_date).filter_by(bookingstatus="Confirmed")
		new_list = []
		for i in bookings_current:
			slots = i.slotx
			latest_slot = max([i.id for i in slots])
			slot_query = Slot.query.filter_by(id=latest_slot).first()
			if current_time < slot_query.end_time:
				new_list.append(i)
		new_list = new_list + [i for i in bookings_future]
		print (new_list)
		# slots = bookings.slotx
		# latest_slot = max([i.id for i in slots])
		# slot_query = Slot.query.filter_by(id=latest_slot).first()
		something = [i.serialize() for i in new_list]
		return jsonify(something)
	except Exception as e:
		return str(e)


@app.route('/cancelbooking/', methods=['PUT'])
def cancel_booking():
	#cancel booking of not past due bookings. --> check with date and time
	#update credits?
	#check that user has bookingref before cancelling
	now = datetime.now()
	current_date = now.strftime("%Y-%m-%d")
	current_time = int(now.strftime("%H%M"))
	chatid = request.json['chatid']
	# email = request.json['email']
	bookingref = request.json['bookingref']
	booking = Booking.query.filter_by(bookingref=bookingref).first()
	
	student = Student.query.filter_by(telegram_chat_id=chatid).first()
	student_bookings = Booking.query.filter_by(student_id=student.id)
	
	try:
		# slot_table = Slot.query.all()
		#get the slots, take the values from slot table. compare with current time.

		if bookingref in [i.bookingref for i in student_bookings]:
			slots = booking.slotx
			if booking.date >= current_date:
				if booking.date == current_date:
					latest_slot = max([i.id for i in slots])
					slot_query = Slot.query.filter_by(id=latest_slot).first()
					if current_time > slot_query.end_time - 30: #return half credits
						credits_return = len([i.id for i in slots])//2
						student.credits = student.credits+credits_return
						# print (student.credits)
						db.session.commit()
						booking.bookingstatus = "Cancelled"
						db.session.commit()
						# print (student.credits)
					else: #return no credits
						booking.bookingstatus = "Cancelled"
						db.session.commit()

					# print (max([i.id for i in slots]))
				else:
					credits_return = len([i.id for i in slots])
					# credits_no = student.credits+credits_return
					# print (credits_no)
					student.credits = student.credits+credits_return
					# print (student.credits)
					db.session.commit()
					booking.bookingstatus = "Cancelled"
					db.session.commit()

				
				return jsonify(booking.serialize())
			else:
				tosend = "Booking date has expired"
				return tosend
		else:
			tosend = "You do not have this booking reference"
			return tosend
	except Exception as e:
		return str(e)

@app.route('/updatepenalty/', methods=['PUT'])
def update_penalty(booking_ref):
	# booking_id = request.json['booking_id']
	student_id = Booking.query.filter_by(bookingref=booking_ref).first().student_id
	student = Student.query.filter_by(id=student_id).first()
	numberPenalty = student.no_of_penalty
	student.no_of_penalty = numberPenalty + 1
	db.session.commit()
	#check if student penalty >= 3
	numberPenalty = student.no_of_penalty
	if numberPenalty >= 3:
		student.status = "Inactive"
		db.session.commit()
		return("Number of penalty successfully updated. \n User penalty is more than or equals to 3, User is banned")
	return ("Number of penalty successfully updated. \n User penalty is less than 3, User is not banned")



