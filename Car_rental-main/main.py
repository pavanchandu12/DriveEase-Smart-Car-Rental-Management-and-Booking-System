from flask import Flask, render_template, request, redirect, url_for, send_from_directory
import pymysql
import datetime
from datetime import date
import math
from time import gmtime, strftime

hostname = 'localhost'
username = 'root'
password = 'chandu@2004'
database = 'car_rental'
myConnection = pymysql.connect(host=hostname, user=username, passwd=password, db=database, autocommit=True,
                               cursorclass=pymysql.cursors.DictCursor, local_infile=True)
print("Database connected")
cursor = myConnection.cursor()
# app = Flask(__name__)
app = Flask(__name__, 
    static_folder='static',  # Add this line
    template_folder='templates'  # Add this line
)

# Add a route for serving static files (optional but can help debug)
@app.route('/static/<path:filename>')
def serve_static(filename):
    return send_from_directory(app.static_folder, filename)

@app.route('/')
def main():
    return render_template('main.html')

@app.route('/upload', methods=['POST'])
def upload():
    operation_type = request.form['carrental']
    query_report = """select v.Owner_id, ct.Car_type, sum(Amount_due) As Earnings
                      from vehicle_owner v
                      join rents r on v.Vehicle_id = r.Vehicle_id
                      join car c on c.Vehicle_id = v.Vehicle_id
                      join cartype ct on ct.type_id = c.type_id
                      where r.Return_date >= sysdate() and r.Return_date <= sysdate() + 7
                      group by v.Owner_id, ct.Car_type"""
    cursor.execute(query_report)
    result = cursor.fetchall()
    if operation_type == "1":
        return render_template('Customer.html')
    elif operation_type == "2":
        return render_template('Car.html')
    elif operation_type == "3":
        return render_template('UpdateRentalRates.html')
    elif operation_type == "4":
        return render_template('reservation.html')
    elif operation_type == "5":
        return render_template('carreturn.html')
    elif operation_type == "6":
        return render_template('report.html', res=result)

@app.route('/selectcustomer', methods=['POST'])
def selectcustomer():
    customer_type = request.form['customer']
    if customer_type == "Individual":
        return render_template('Individual.html')
    elif customer_type == "Company":
        return render_template('Company.html')

@app.route('/Individual', methods=['POST'])
def Individual():
    cutsomer_type = "Individual"
    intial = request.form['intial']
    lastname = request.form['LastName']
    phoneno = request.form['phone']
    query = "Insert into customer (Phone, Customer_type, Initial, Lname) values (%s, %s, %s, %s)"
    status = cursor.execute(query, (phoneno, cutsomer_type, intial, lastname))
    myConnection.commit()
    if status > 0:
        return render_template('Main.html')
    else:
        return "Error in insertion"

@app.route('/Car', methods=['POST'])
def Car():
    model = request.form['model']
    year = int(request.form['year'])  # Year should be an integer
    cartype = request.form['cars']
    owner_id = request.form['owner_id']
    
    # Fetch the type_id for the given car type
    type_fetchquery = "SELECT type_id FROM cartype WHERE Car_type = %s"
    cursor.execute(type_fetchquery, (cartype,))
    results = cursor.fetchone()
    
    if results is None:
        return "Error: Car type not found", 400
    
    type_id = results['type_id']
    
    # Insert the car details into the car table without Vehicle_id
    query = "INSERT INTO car (Model, Year, Type_id) VALUES (%s, %s, %s)"
    status = cursor.execute(query, (model, year, type_id))
    myConnection.commit()
    
    if status > 0:
        print("Car Insertion Successful")
    else:
        return "Error in car insertion", 500

    # Fetch the Vehicle_id of the newly inserted car
    getvehicleid_query = "SELECT LAST_INSERT_ID() AS Vehicle_id"
    cursor.execute(getvehicleid_query)
    vehicle_id_result = cursor.fetchone()
    
    Vehicle_id = vehicle_id_result['Vehicle_id']

    # Insert the owner details into the vehicle_owner table
    query = "INSERT INTO vehicle_owner (Vehicle_id, Owner_id) VALUES (%s, %s)"
    status = cursor.execute(query, (Vehicle_id, owner_id))
    myConnection.commit()
    
    if status > 0:
        print("Owner Insertion Successful")
    else:
        return "Error in owner insertion", 500

    # Set availability dates for the vehicle
    Available_start = datetime.datetime.now()
    Available_end = Available_start + datetime.timedelta(days=30)
    
    q1 = "INSERT INTO availability (Vehicle_id, Available_start, Available_end) VALUES (%s, %s, %s)"
    stat1 = cursor.execute(q1, (Vehicle_id, Available_start, Available_end))
    myConnection.commit()
    
    if stat1 > 0:
        print("Availability Insertion Successful")
    else:
        return "Error in availability insertion", 500
    
    return render_template('Main.html')


@app.route('/Carreturn', methods=['POST'])
def carreturn():
    customer1_id = request.form['cid']
    q2 = """select * from rents r
            join customer c on c.Idno = r.customer_id
            where Customer_id = %s"""
    cursor.execute(q2, (customer1_id,))
    stat2 = cursor.fetchall()
    if not stat2:
        return "No vehicle has been booked under you"
    else:
        return render_template('reservation_details.html', res=stat2, customerid=customer1_id)

@app.route('/deletereservation', methods=['POST'])
def deletereservation():
    list = request.form.getlist('returncar')
    cust_id = request.form['custid']
    for vehicle_id in list:
        dele_query = "delete from rents where Customer_id = %s and Vehicle_id = %s"
        cursor.execute(dele_query, (cust_id, vehicle_id))
        myConnection.commit()

        Available_start1 = datetime.datetime.now()
        qn = "update availability set Available_start = %s where Vehicle_id = %s"
        cursor.execute(qn, (Available_start1, vehicle_id))
        myConnection.commit()

    return render_template('Main.html')

@app.route('/reservation', methods=['POST'])
def reservation():
    cartype1 = request.form['cars']
    start = request.form['startdate']
    end = request.form['enddate']
    q5 = """select * from car c
            join cartype ct on c.Type_id = ct.Type_id
            join availability a on c.Vehicle_id = a.Vehicle_id
            where a.Available_start <= %s and a.Available_end >= %s and ct.car_type = %s"""
    cursor.execute(q5, (start, end, cartype1))
    stat5 = cursor.fetchall()
    if not stat5:
        return "No cars available"
    else:
        return render_template('booking.html', res=stat5, start=start, end=end, car_type=cartype1)

@app.route('/booking', methods=['POST'])
def booking():
    veh = request.form['bookcar']
    cid = request.form['custid']
    stdate = request.form['sdate']
    retdate = request.form['rdate']
    rental_type = request.form['rentalype']
    
    # Get the daily and weekly rates from the form data
    wr = float(request.form['Weekly_rate'])
    dr = float(request.form['Daily_rate'])

    # Parse the start and return dates
    sdate_value = datetime.datetime.strptime(stdate, "%Y-%m-%d")
    rdate_value = datetime.datetime.strptime(retdate, "%Y-%m-%d")

    active = 1
    scheduled = 0
    no_days = 0
    no_wk = 0
    amount_due = 0

    # Calculate amount due based on rental type
    if rental_type == "1":  # Weekly rental
        no_wk = math.ceil(abs((rdate_value - sdate_value).days / 7))
        amount_due = no_wk * wr
    elif rental_type == "2":  # Daily rental
        no_days = abs((rdate_value - sdate_value).days)
        amount_due = no_days * dr

    # Check if the start date is in the future
    if sdate_value.date() > datetime.datetime.today().date():
        active = 0
        scheduled = 1

    # Adjusted SQL Insert statement with explicit column names
    q6 = """
    INSERT INTO RENTS (Customer_id, Vehicle_id, Start_date, Return_date, Amount_due, Noofdays, Noofweeks, Dailyrent, Weeklyrent, Active, Scheduled)
    VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
    """
    
    # Execute the SQL command with values including daily and weekly rates
    cursor.execute(q6, (cid, veh, stdate, retdate, amount_due, no_days, no_wk, dr, wr, active, scheduled))
    myConnection.commit()

    # Update the availability of the vehicle
    Available_start2 = rdate_value + datetime.timedelta(days=1)
    q7 = "UPDATE availability SET Available_start = %s WHERE Vehicle_id = %s"
    cursor.execute(q7, (Available_start2, veh))
    myConnection.commit()

    return render_template('Main.html')


@app.route('/CompanyInsertion', methods=['POST'])
def CompanyInsertion():
    cutsomer_type = "Company"
    cname = request.form['Cname']
    phoneno = request.form['phone']
    query = "insert into customer (Phone, Customer_type, Cname) values (%s, %s, %s)"
    status = cursor.execute(query, (phoneno, cutsomer_type, cname))
    myConnection.commit()
    if status > 0:
        return render_template('Main.html')
    else:
        return "Error in insertion"

@app.route('/UpdateRental', methods=['POST'])
def UpdateRental():
    car_type = request.form['cars']
    weekly_rate = float(request.form['weekly'])
    daily_rate = float(request.form['daily'])
    type_fetchquery = "select type_id from cartype where Car_type = %s"
    cursor.execute(type_fetchquery, (car_type,))
    results = cursor.fetchall()[0]
    type_id = int(results['type_id'])
    query_update = "Update cartype set Weekly_rate = %s, Daily_rate = %s where Type_id = %s"
    status = cursor.execute(query_update, (weekly_rate, daily_rate, type_id))
    myConnection.commit()
    if status > 0:
        print("Update Successful")
    else:
        print("Error in update")
    return render_template('Main.html')

if __name__ == '__main__':
    app.run('127.0.0.1', 9000)
