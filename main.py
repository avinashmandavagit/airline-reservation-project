import re
import os
import datetime
import boto3 as boto3
from datetime import datetime, timedelta
import pymysql as pymysql
from flask import Flask, request, render_template, session, redirect
app = Flask(__name__)
airline_region_name = 'us-east-2'
airline_bucket = "airlinereservation"
airline_email_s3 = 'mandavaavi@gmail.com'
s3_client_airline = boto3.client('s3', aws_access_key_id="AKIAWFRKXCS4WNN35DEI", aws_secret_access_key="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")
ses_client_airline = boto3.client('ses', aws_access_key_id="AKIAWFRKXCS4WNN35DEI", aws_secret_access_key="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", region_name=airline_region_name)
# conn = pymysql.connect(host="localhost", user="root", password="Venu@123", db="Airline_Reservation_System")
conn = pymysql.connect(host="airline-rds.cthh2hds7mbn.us-east-1.rds.amazonaws.com", user="admin", password="admin123", db="Airline_Reservation_System")
cursor = conn.cursor()

admin_username = 'admin'
admin_password = 'admin'
app.secret_key = 'fjsfdfd'
APP_ROOT = os.path.dirname(os.path.abspath(__file__))
APP_ROOT = APP_ROOT+'/static/'



@app.route("/")
def index():
    return render_template("index.html")


@app.route("/logout")
def logout():
    session.clear()
    return redirect("/")


@app.route("/admin_login")
def admin_login():
    return render_template("admin_login.html")


@app.route("/admin_login1", methods=['post'])
def admin_login1():
    user_name = request.form.get("username")
    password = request.form.get("password")
    if user_name == admin_username and password == admin_password:
        session['role'] = 'admin'
        return render_template("admin_home.html")
    else:
        return render_template("msg.html", message="invalid login details")


@app.route("/admin_home")
def admin_home():
    return render_template("admin_home.html")


@app.route("/customer_login")
def customer_login():
    return render_template("customer_login.html")


@app.route("/customer_login1", methods=['post'])
def customer_login1():
    email = request.form.get('email')
    password = request.form.get('password')
    count = cursor.execute("select * from customer where email= '" + str(email) + "' and password = '" + str(password) + "'")
    if count > 0:
        customers = cursor.fetchall()
        customer_login_emails = ses_client_airline.list_identities(
            IdentityType='EmailAddress'
        )
        if email in customer_login_emails['Identities']:
            customer_lofin_info = 'You' + '' + ' have Sucessfully Logged In to Airline Website'
            ses_client_airline.send_email(Source=airline_email_s3, Destination={'ToAddresses': [email]},
                                            Message={'Subject': {'Data': customer_lofin_info, 'Charset': 'utf-8'},
                                                     'Body': {'Html': {'Data': customer_lofin_info, 'Charset': 'utf-8'}}})
            customer = customers[0]
            session["customer_id"] = customer[0]
            session["role"] = 'customer'
            return redirect("/customer_home")
    else:
        return render_template("msg.html", message="Invalid Login Details")


@app.route("/customer_home")
def customer_home():
    customer_id = session['customer_id']
    cursor.execute("select * from customer where customer_id='"+str(customer_id)+"'")
    customers = cursor.fetchall()
    return render_template("customer_home.html", customers=customers)


@app.route("/customer_registration")
def customer_registration():
    return render_template("customer_registration.html")


@app.route("/customer_registration1", methods=['post'])
def customer_registration1():
    name = request.form.get('name')
    phone = request.form.get('phone')
    email = request.form.get('email')
    password = request.form.get('password')
    gender = request.form.get("gender")
    address = request.form.get("address")
    count = cursor.execute("select * from customer where email= '" + str(email) + "' or phone = '" + str(phone) + "'")
    if count == 0:
        customer_emails = ses_client_airline.list_identities(
            IdentityType='EmailAddress'
        )
        if email in customer_emails['Identities']:
            customer_send = 'Hi' + '' + name + ' You Have Registered Sucessfully into the Airline Website'
            ses_client_airline.send_email(Source=airline_email_s3, Destination={'ToAddresses': [email]},
                                            Message={'Subject': {'Data': customer_send, 'Charset': 'utf-8'},
                                                     'Body': {'Html': {'Data': customer_send, 'Charset': 'utf-8'}}})
            cursor.execute("insert into customer(name,phone,email,password,gender,address) values('" + str(name) + "', '" + str(phone) + "', '" + str(email) + "', '" + str(password) + "', '" + str(gender) + "', '" + str(address) + "')")
            conn.commit()
            return render_template("msg.html", message="Customer Registered Successfully")
        else:
            return render_template("msg.html", message="Your email is not verified by website.")
    else:
        return render_template("msg.html", message="Duplicate Details")

@app.route("/customer_email_verification")
def customer_email_verification():
    return render_template("customer_email_verification.html")

@app.route("/customer_email_verification1")
def customer_email_verification1():
    email = request.args.get("email")
    ses_client_airline.verify_email_address(
        EmailAddress=email
    )
    return render_template("msg.html", message="Click on the link that sent to your emailaddress")


@app.route("/airports")
def airports():
    cursor.execute("select * from airport")
    airports = cursor.fetchall()
    return render_template("airports.html", airports=airports)


@app.route("/add_airport", methods=['post'])
def add_airport():
    airport_name = request.form.get("airport_name")
    airport_code = request.form.get("airport_code")
    count = cursor.execute("select * from airport where airport_code= '" + str(airport_code) + "' or airport_name = '" + str(airport_name) + "'")
    if count > 0:
        return render_template("msg.html", message="This Airport Name Already Added", color="text-danger")
    else:
        cursor.execute("insert into airport(airport_name,airport_code) values('" + str(airport_name) + "', '" + str(airport_code) + "')")
        conn.commit()
    return redirect("/airports")


@app.route("/airplanes")
def airplanes():
    query = ""
    from_airport_name = request.args.get("from_airport_name")
    to_airport_name = request.args.get("to_airport_name")
    search_date = request.args.get("search_date")

    if search_date == None or search_date == '':
        print('fggh')
        search_date = datetime.today().strftime("%Y-%m-%d")
    if from_airport_name == None or to_airport_name == None:
        query = "select * from airplane"
    if (from_airport_name == '' and to_airport_name == '') and search_date == '':
        query = "select * from airplane where airplane_id in(select airplane_id from flight)"
    elif (from_airport_name == '' and to_airport_name == '') and search_date != '':
        query = "select * from airplane where airplane_id in(select airplane_id from flight where search_date = '"+str(search_date)+"')"
    elif (from_airport_name != '' and to_airport_name != '') and search_date == '':
        query = "select * from airplane where airplane_id in(select airplane_id from flight where from_airport = '%" + str(from_airport_name) + "%' and to_airport = '%" + str(to_airport_name) + "%')"
    elif (from_airport_name != '' and to_airport_name != '') and search_date != '':
        query = "select * from airplane where airplane_id in(select airplane_id from flight where from_airport = '%" + str(from_airport_name) + "%' and to_airport = '%" + str(to_airport_name) + "%' and search_date = '" + str(search_date) + "')"
    if session['role'] == 'admin':
        query = "select * from airplane"
    cursor.execute(query)
    airplanes = cursor.fetchall()
    message = ""
    return render_template("airplanes.html", airplanes=airplanes, search_date=search_date,to_airport_name=to_airport_name,from_airport=from_airport_name,message=message)


@app.route("/add_airplane")
def add_airplane():
    return render_template("add_airplane.html")


@app.route("/add_airplane1", methods=['post'])
def add_airplane1():
    airplane_name = request.form.get("airplane_name")
    airplane_number = request.form.get("airplane_number")
    first_class_seats = request.form.get("first_class_seats")
    business_class_seats = request.form.get("business_class_seats")
    economy_class_seats = request.form.get("economy_class_seats")
    picture = request.files.get("picture")
    path = APP_ROOT + "/" + picture.filename
    picture.save(path)
    s3_client_airline.upload_file(path, airline_bucket, picture.filename)
    picture_s3_file_name = picture.filename
    picture_image_url = f'https://{airline_bucket}.s3.amazonaws.com/{picture_s3_file_name}'

    count = cursor.execute("select * from airplane where airplane_number= '" + str(airplane_number) + "'")
    if count > 0:
        return render_template("msg.html", message="Airplane Number Must Be Unique Number", color="text-danger")
    else:
        cursor.execute("insert into airplane(airplane_name,airplane_number,first_class_no_of_seats,business_class_no_of_seats,economy_class_no_of_seats,picture) values('" + str(airplane_name) + "', '" + str(airplane_number) + "', '" + str(first_class_seats) + "', '" + str(business_class_seats) + "', '" + str(economy_class_seats) + "', '" + str(picture_image_url) + "')")
        conn.commit()
    return redirect("/airplanes")


@app.route("/add_flight")
def add_flight():
    airplane_id = request.args.get("airplane_id")
    cursor.execute("select * from airport")
    airports = cursor.fetchall()
    airports = list(airports)
    return render_template("add_flight.html", airplane_id=airplane_id, airports=airports)


@app.route("/add_flight1", methods=['post'])
def add_flight1():
    airplane_id = request.form.get("airplane_id")

    from_airport = request.form.get("from_airport")
    cursor.execute("select * from airport where airport_id = '"+str(from_airport)+"' ")
    airport = cursor.fetchall()
    from_airport_name = airport[0][1]

    to_airport = request.form.get("to_airport")
    cursor.execute("select * from airport where airport_id = '" + str(to_airport) + "' ")
    airport = cursor.fetchall()
    to_airport_name = airport[0][1]

    first_class_price = request.form.get("first_class_price")
    business_class_price = request.form.get("business_class_price")
    economy_class_price = request.form.get("economy_class_price")
    departure = request.form.get("departure")
    arrival = request.form.get("arrival")
    gate_number = request.form.get("gate_number")
    date = datetime.now()
    departure = departure.replace("T", " ")
    arrival = arrival.replace("T", " ")
    departure = datetime.strptime(departure, '%Y-%m-%d %H:%M')
    arrival = datetime.strptime(arrival, '%Y-%m-%d %H:%M')
    search_date = departure.date()
    search_date = search_date.strftime('%Y-%m-%d')
    print(type(search_date))

    if departure > arrival:
        return render_template("msg.html", message="Invalid Arrival Time", color="text-danger")
    cursor.execute("insert into flight(airplane_id,from_airport_id,from_airport,to_airport,to_airport_id,first_class_price,business_class_price,economy_class_price,despature,arrival,date,gate_number,search_date) values('" + str(airplane_id) + "', '" + str(from_airport) + "', '" + str(from_airport_name) + "', '" + str(to_airport_name) + "', '" + str(to_airport) + "', '" + str(first_class_price) + "', '" + str(business_class_price) + "', '" + str(economy_class_price) + "', '" + str(departure) + "', '" + str(arrival) + "', '" + str(date) + "', '" + str(gate_number) + "', '" + str(search_date) + "' )")
    conn.commit()
    return render_template("msg.html", message="Flight Added Successful", color="text-success")


@app.route("/view_flights")
def view_flights():
    airplane_id = request.args.get("airplane_id")
    cursor.execute("select * from flight where airplane_id = '" + str(airplane_id) + "' ")
    flights = cursor.fetchall()
    flights = list(flights)
    if len(flights) == 0:
        return render_template("msg.html", message="Flights Not Available", color="text-danger")
    return render_template("view_flights.html", int=int, get_booked_seats_by_flight_id=get_booked_seats_by_flight_id, flights=flights, get_airplane_id=get_airplane_id, get_from_airport_id=get_from_airport_id, get_to_airport_id=get_to_airport_id)


def get_airplane_id(airplane_id):
    print(airplane_id)
    cursor.execute("select * from airplane where airplane_id = '" + str(airplane_id) + "' ")
    airplane = cursor.fetchall()
    print(airplane)
    return airplane[0]


def get_from_airport_id(from_airport):
    cursor.execute("select * from airport where airport_id = '" + str(from_airport) + "' ")
    from_airport = cursor.fetchall()
    return from_airport[0]


def get_to_airport_id(to_airport):
    cursor.execute("select * from airport where airport_id = '" + str(to_airport) + "' ")
    to_airport = cursor.fetchall()
    return to_airport[0]

def get_airplane_id_by_flight_id(flight_id):
    cursor.execute("select * from airplane where airplane_id in(select airplane_id from flight where flight_id = '" + str(flight_id) + "')")
    airplane = cursor.fetchall()
    return airplane[0]


@app.route("/book_seats")
def book_seats():
    flight_id = request.args.get("flight_id")
    cursor.execute("select * from flight where flight_id = '" + str(flight_id) + "' ")
    flight = cursor.fetchall()
    flight = flight[0]
    class_type = request.args.get("class_type")
    seat_numbers = request.args.get("seat_numbers")
    amount = request.args.get("amount")
    return render_template("book_seats.html", int=int, get_seats_booking_id=get_seats_booking_id, flight_id=flight_id, flight=flight, get_airplane_id=get_airplane_id, class_type=class_type, seat_numbers=seat_numbers, amount=amount,get_airplane_id_by_flight_id=get_airplane_id_by_flight_id)


@app.route("/book_seats1", methods=['post'])
def book_seats1():
    flight_id = request.form.get("flight_id")
    cursor.execute("select * from flight where flight_id = '" + str(flight_id) + "' ")
    flight = cursor.fetchall()
    class_type = request.form.get("class_type")
    seat_numbers = request.form.get("seat_numbers")
    amount = request.form.get("amount")
    customer_id = session['customer_id']
    date = datetime.now()
    status = 'Payment Pending'
    no_of_seats = []
    total_amount = 0

    for i in range(1, int(seat_numbers)+1):
        seat_number = request.form.get("seat_number" + str(i))
        if seat_number!= None:
            no_of_seats.append(seat_number)

    total_amount = len(no_of_seats) * int(amount)
    no_of_seats = list(no_of_seats)
    if len(no_of_seats) == 0:
        return render_template("msg.html", message='Choose Seats', color='text-primary')
    for no_of_seat in no_of_seats:
        # print("insert into bookings(flight_id,customer_id,class_type,total_amount,date,seat_numbers,status) values('" + str(flight_id) + "', '" + str(customer_id) + "', '" + str(class_type) + "', '" + str(total_amount) + "', '" + str(date) + "', '" + str(no_of_seat) + "', '" + str(status) + "')")
        cursor.execute("insert into bookings(flight_id,customer_id,class_type,total_amount,date,seat_numbers,status) values('" + str(flight_id) + "', '" + str(customer_id) + "', '" + str(class_type) + "', '" + str(total_amount) + "', '" + str(date) + "', '" + str(no_of_seat) + "', '" + str(status) + "')")
        conn.commit()
        booking_id = cursor.lastrowid
        cursor.execute("select * from bookings where booking_id = '" + str(booking_id) + "' ")
        bookings = cursor.fetchall()
        print(bookings)
        print(flight)
        return render_template("book_seat1.html", bookings=bookings, flight=flight[0], get_airplane_id=get_airplane_id,  get_customer_id=get_customer_id, class_type=class_type)


def get_seats_booking_id(flight_id, i, class_type):
    cursor.execute("select * from bookings where flight_id = '" + str(flight_id) + "' and class_type = '" + str(class_type) + "' ")
    bookings = cursor.fetchall()
    for booking in bookings:
        if str(i) in booking[5]:
            return True
    return False


def get_customer_id(customer_id):
    cursor.execute("select * from customer where customer_id = '" + str(customer_id) + "' ")
    customer = cursor.fetchall()
    return customer[0]


@app.route("/pay_amount", methods=['post'])
def pay_amount1():
    booking_id = request.form.get("booking_id")
    amount = request.form.get("amount")
    card_number = request.form.get("card_number")
    holder_name = request.form.get("holder_name")
    date = datetime.now()
    status = "Transaction Successfully Completed"
    cursor.execute("insert into payment(booking_id,amount,card_number,holder_name,date,status) values('" + str(booking_id) + "', '" + str(amount) + "', '" + str(card_number) + "', '" + str(holder_name) + "', '" + str(date) + "', '" + str(status) + "')")
    conn.commit()
    cursor.execute("update bookings set status ='Seat Booked by Customer' where booking_id = '"+str(booking_id)+"'")
    conn.commit()
    cursor.execute("select * from bookings where booking_id = '"+str(booking_id)+"'")
    booking = cursor.fetchall()
    seat_numbers = booking[0][5]
    i = 0
    for seat_number in seat_numbers:
        passenger_name = request.form.get('passenger_name' + str(i))
        from_airport = request.form.get("from_airport")
        cursor.execute("select * from airport where airport_id = '"+str(from_airport)+"'")
        airport = cursor.fetchall()
        from_airport = airport[0][1]
        to_airport = request.form.get("to_airport")
        cursor.execute("select * from airport where airport_id = '" + str(to_airport) + "'")
        airport = cursor.fetchall()
        to_airport = airport[0][1]
        departure = request.form.get("departure")
        departure = datetime.strptime(departure, '%Y-%m-%d %H:%M:%S')
        gate_number = request.form.get("gate_number")
        boarding_time = departure - timedelta(hours=1)
        cursor.execute("insert into boarding_pass(booking_id,passenger_name,seat_number,from_airport,to_airport,gate_number,boarding_time) values('" + str(booking_id) + "', '" + str(passenger_name) + "', '" + str(seat_number) + "', '" + str(from_airport) + "', '" + str(to_airport) + "', '" + str(gate_number) + "', '"+str(boarding_time)+"')")
        conn.commit()
        i = i + 1
    return render_template("msg.html", message='Transaction Successfully and Booking Seats Are Confirmed', color='text-primary')


@app.route("/view_bookings")
def view_bookings():
    query = ""
    flight_id = request.args.get("flight_id")
    if session['role'] == "admin":
        flight_id = request.args.get("flight_id")
        query = "select * from bookings where flight_id = '"+str(flight_id)+"' and status != 'Payment Pending'"
    elif session['role'] == "customer":
        customer_id = session['customer_id']
        query = "select * from bookings where flight_id = '" + str(flight_id) + "' and status != 'Payment Pending' and customer_id = '"+str(customer_id)+"'"
    cursor.execute(query)
    bookings = cursor.fetchall()
    bookings = list(bookings)
    if len(bookings) == 0:
        return render_template("msg.html", message="Bookings Not Available", color="text-danger")
    return render_template("view_bookings.html", bookings=bookings, get_flight_id=get_flight_id, get_from_airport_id=get_from_airport_id, get_to_airport_id=get_to_airport_id, get_airplane_id=get_airplane_id, get_customer_id=get_customer_id)


@app.route("/view_boarding_pass")
def view_boarding_pass():
    booking_id = request.args.get("booking_id")
    cursor.execute("select * from boarding_pass where booking_id = '" + str(booking_id) + "'")
    boarding_passes = cursor.fetchall()
    boarding_passes = list(boarding_passes)
    if len(boarding_passes) == 0:
        return render_template("msg.html", message="Boarding Passes Not Available", color="text-danger")
    return render_template("view_boarding_pass.html", get_flight_id=get_flight_id, get_airplane_id=get_airplane_id, boarding_passes=boarding_passes, get_booking_id= get_booking_id, get_customer_id=get_customer_id)


@app.route("/boarding_pass")
def boarding_pass():
    cursor.execute("select * from boarding_pass")
    boarding_passes = cursor.fetchall()
    return render_template("view_boarding_pass.html", get_flight_id=get_flight_id, get_airplane_id=get_airplane_id, boarding_passes=boarding_passes, get_booking_id= get_booking_id, get_customer_id=get_customer_id, get_airplane_by_airplane_id=get_airplane_by_airplane_id)


def get_booking_id(booking_id):
    cursor.execute("select * from bookings where booking_id = '" + str(booking_id) + "'")
    booking = cursor.fetchall()
    return booking[0]

def get_airplane_by_airplane_id(airplane_id):
    cursor.execute("select * from airplane where airplane_id = '" + str(airplane_id) + "' ")
    airplane = cursor.fetchall()
    print(airplane)
    return airplane[0]


def get_flight_id(flight_id):
    cursor.execute("select * from flight where flight_id = '" + str(flight_id) + "'")
    flight = cursor.fetchall()
    return flight[0]


@app.route("/view_payments")
def view_payments():
    booking_id = request.args.get("booking_id")
    cursor.execute("select * from payment where booking_id = '" + str(booking_id) + "'")
    payments = cursor.fetchall()
    payments = list(payments)
    if len(payments) == 0:
        return render_template("msg.html", message="Payments Not Available", color="text-danger")
    return render_template("view_payments.html", payments=payments, get_customer_id=get_customer_id, get_booking_id=get_booking_id)


def get_booked_seats_by_flight_id(flight_id, class_type):
    cursor.execute("select * from boarding_pass where booking_id in(select booking_id from bookings where flight_id  = '"+str(flight_id)+"' and status = 'Seat Booked by Customer' and class_type = '"+str(class_type)+"')")
    booked_seats = cursor.fetchall()
    print(booked_seats)
    booked_seats = len(booked_seats)
    return booked_seats


@app.route("/cancel_booking")
def cancel_booking():
    booking_id = request.args.get("booking_id")
    cursor.execute("update bookings set status ='Seat Cancelled by Customer' where booking_id = '" + str(booking_id) + "'")
    conn.commit()
    return render_template("msg.html", message='Booking Cancelled by Customer', color="danger")


app.run(debug=True)