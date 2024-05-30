from flask import Flask, render_template
from flask import Flask, request, redirect, url_for ###for request and response
from flask_restful import Resource, Api #For rest api
import psycopg2 #for postgres sql
from flask import Flask, render_template, request, redirect, url_for, flash, session
from flask import Flask, jsonify
import serial
import time
import random

counter= 0
app = Flask(__name__)
api = Api(app) #creating the for api

############# database connectivity#############################################################
def connect_db():
    return psycopg2.connect(
        dbname="postgres",
        user="postgres",
        password="admin",
        host="localhost"
    )
############################################Arduino Code######################################################################################

@app.route('/api/read_sensors')
def read_sensors():
 try:
    # ser = serial.Serial('COM9', 9600, timeout=1)
    print('Serial is ok')
    #ser.flush()
    print('serial flush ok')
    # line = ser.readline().decode('utf-8').rstrip()
    #print("Line",line)
    if True: # if ser.in_waiting > 0:
        # line = ser.readline().decode('utf-8').rstrip()
        # print('line print okay',line)
        # humidity, temperature, gasValue, locationID = line.split(",")
        global counter
        th = 20
        tt = 400
        tg = 500
        h = counter +1
        t= counter +5
        g= counter +7
        counter +=1
        if counter>50:
            counter=0
       # h = float (random.uniform(5, 50))# h = float(humidity)
        #t = float (random.uniform(20, 60))# t = float(temperature)
        #g = float (random.uniform(5, 100))# g = float(gasValue)
        locationID = 3# locationID =int (locationID) to generate alert to specific location need to check from DB
        print('readSensor output',"H= ",h,"t=",t,"g=",g)
        try:
            conn = connect_db()
            cur = conn.cursor()
            if h > th or t >tt or g> tg: 
                print('Threashold hit##########################################')
                #cur.execute('UPDATE public."labormonitoring" SET status = %s, color = %s WHERE id = %s' ,
                #        (5, '#FF0000', locationID))
                cur.execute('UPDATE public."labormonitoring" SET status = %s, color = %s WHERE id = %s OR "locationID" = %s',
            (5, '#FF0000', locationID, locationID))
            cur.execute(
                'INSERT INTO public."sensorLocationTable" (humidity, temp, gas, id,timestamp) VALUES (%s, %s, %s, %s,%s)',
                (h, t, g, locationID,time.time())
            )
            conn.commit()
            cur.close()
            conn.close()
            return jsonify({"status": "Success", "message": "Data inserted successfully."})
        except Exception as e:
            print('Error occurred',e)
            return jsonify({"status": "Error", "message": str(e)})
 except serial.serialutil.SerialException as e:
     print(f"Error opening serial port: {e}")
 finally:
     print('END')
        # ser.close()



##################################################################################################################################
##############################Labor employee login###########################################################################################

#########################################################################################################################
###############################Mobile Login Page###################################################################################################

@app.route('/loginEmployee', methods=['GET', 'POST'])
def loginEmployee():
    print('In login employee page')
    error = None
    if request.method == 'POST':
        print('data received') 
        data = request.get_json()
        username = data.get('username')
        password = data.get('password')
        print('username', username)
        print('password', password)
        conn = connect_db()
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM public.labormonitoring WHERE name=%s AND password=%s", (username, password))
        print("cursor\t", cursor)
        user = cursor.fetchone()
        print("User Name:",user[1])
        cursor.close()
        conn.close()

        if user:
            conn = connect_db()
            cursor = conn.cursor()
            update_query = 'UPDATE labormonitoring SET \"liveStatus\" = TRUE WHERE name = %s'
            cursor.execute(update_query, (username,))
            conn.commit()
            return jsonify({'message': 'Login successful'}), 200
        
        else:
            return jsonify({'message': 'Invalid credentials'}), 401

    return render_template('loginEmployee.html')

@app.route('/api/logout',methods=['GET','POST'])
def logout():
        if request.method == 'POST':
            print('data received') 
            data = request.get_json()
            username = data.get('username')
            conn = connect_db()
            cursor = conn.cursor()
            update_query = 'UPDATE labormonitoring SET \"liveStatus\" = FALSE WHERE name = %s'
            cursor.execute(update_query, (username,))
            conn.commit()
            return jsonify({'message': 'Login successful'}), 200
        return jsonify({'message': 'Invalid credentials'}), 401
######################################Puerly Mobile Development###############################################################################################
@app.route('/api/updateLocation', methods=['POST']) #this function is used in mobile application when the page is accessed by the
#mobile then user is continiously updating the position 
def updateLocation():
    print('Called updatedLocation')
    # Ensure the request is JSON and has the required fields
    if not request.is_json:
        return jsonify({"error": "Request must be JSON"}), 400
    
    data = request.get_json()
    latitude = data.get('lat')
    longitude = data.get('lng')
    pUsername = data.get('username')
    print('latitude as :',latitude,'Longitude as :',longitude,'username',pUsername)
    if latitude is None or longitude is None:
        return jsonify({"error": "Missing latitude or longitude in request"}), 400
    elif not pUsername or pUsername.isspace() or not pUsername.isalpha():
        print("Error: Invalid username. relogin and try again.")
        return
    print('Going to update the userLocation',pUsername)
    conn = connect_db()
    cursor = conn.cursor()
    try:
        update_query = "UPDATE labormonitoring SET longitude = %s, latitude = %s WHERE name = %s;"
        cursor.execute(update_query, (longitude, latitude, pUsername))    
        conn.commit()
            
            # Check if any row is updated
        if cursor.rowcount == 0:
                print("No matching user found to update.")
        else:
                print("Location updated successfully.")
    except Exception as e:
        print("An error occurred:", e)
    finally:
        # Close the database connection
        cursor.close()
    return jsonify({"success": True, "latitude": latitude, "longitude": longitude}), 200


@app.route('/mobileLogin', methods=['GET', 'POST'])
def mobileLogin():
    print('Mobile Login')
    error = None
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        conn = connect_db()
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM public.labormonitoring WHERE name=%s AND password=%s", (username, password))
        print("cursor\t"+cursor)
        user = cursor.fetchone()
        print('User Login'+ user)
        print("User Name:"+user[1])
        cursor.close()
        conn.close()

        if user:
           
            return  render_template('mobileMonitor.html')
        
        else:
             flash('Invalid username or password')

    return render_template('mobileLogin.html')

@app.route('/mobileLocation', methods=['GET', 'POST'])
def mobileLocation():
    print('Mobile Location Called')
    if request.method == 'POST':
        # Handle login logic here
        return "Login logic handled"
    else:
        # For GET requests, return the login page
        return render_template('mobileLocation.html')

@app.route('/signalService', methods=['GET'])
def signal_service():
    print('signal service')
    username = request.args.get('username')
    if not username:
        return jsonify({'error': 'Username is required'}), 400

    try:
        # Connect to your database        # Create a cursor object
        conn = connect_db()
        cursor = conn.cursor()

        # Execute a query
        cursor.execute("SELECT status FROM public.labormonitoring WHERE name = %s", (username,))

        # Fetch one result
        row = cursor.fetchone()
        if row:
            status = row[0]
            alert_signal = status == 5
            return jsonify({'alertSignal': alert_signal})
        else:
            return jsonify({'error': 'User not found'}), 404

    except Exception as e:
        print(e)
        return jsonify({'error': 'An error occurred accessing the database'}), 500

    finally:
        if conn:
            cursor.close()
            conn.close()

###############################Login API###############################################################
#@app.route('/login', methods=['GET', 'POST'])
@app.route('/', methods=['GET', 'POST'])
def login():
    error = None
    print('Dashboard login Executed')
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']

        conn = connect_db()
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM public.labormonitoring WHERE name=%s AND password=%s", (username, password))
        #print("cursor\t"+cursor)
        user = cursor.fetchone()
        #print("User Name:"+user[1])
        cursor.close()
        conn.close()

        if user:
            before_first()
            return  render_template('index.html')
        else:
             flash('Invalid username or password')

    return render_template('login.html')

#################Labor Location##############################################################################
@app.route('/api/locations')
def locations():
    conn = connect_db()
    cursor = conn.cursor()
    #cursor.execute('SELECT * FROM public.labormonitoring WHERE "labormonitoring"."isLocation" = %s', (True,))
    #cursor.execute('SELECT * FROM public."locationTable"')
    cursor.execute('SELECT * FROM public.labormonitoring WHERE "labormonitoring"."liveStatus" = %s', (True,))
    
    labors = cursor.fetchall()
   # print('labor details:',labors)
    cursor.close()
    conn.close()
    for labor in labors:
     print("id", labor[5], "latitude",  labor[2], "longitude",  labor[3],"isLocation",  labor[4],"color", labor[8]) 
    return jsonify([{"id": labor[5], "latitude": labor[2], "longitude": labor[3],"isLocation": labor[4],"color":labor[8]} for labor in labors])

@app.route('/location')
def location_page():
    return render_template('locations.html')


###############################################################################################################
###############################################Real time mobile application################################################################


@app.route('/mobileLocation1')
def mobileLocation1():
    return render_template('mobilemonitor.html')
################################################Initialize location for all #################################################################################
def initilizeLocation():
    print('location initilization')
    conn = connect_db()
    cursor = conn.cursor()
    
    try:
        # Update the row with id = 2, setting isLocation to false
        #public.labormonitoring WHERE "labormonitoring"."isLocation"
        update_query = 'UPDATE labormonitoring SET "locationID" = 0;'
        cursor.execute(update_query)


        # Commit the changes to the database
        conn.commit()
        
        # Check if the update was successful
        if cursor.rowcount == 0:
            print("No rows were updated.")
        else:
            print(f"{cursor.rowcount} row(s) were updated.")
            
    except Exception as e:
        print(f"An error occurred: {e}")
        conn.rollback()  # Rollback the transaction on error
    finally:
        cursor.close()
        conn.close()

#############################################Update the location of the labor#######################################################################################
def update_labormonitoring(id, locationID):
    conn = connect_db()
    cursor = conn.cursor()
    
    try:
        # Update the row with id = 2, setting isLocation to false
        #public.labormonitoring WHERE "labormonitoring"."isLocation"
        update_query = 'UPDATE labormonitoring SET "locationID" = %s WHERE "isLocation" = FALSE AND "id" = %s;'
        update_values = (locationID, id)

        cursor.execute(update_query, update_values)


        # Commit the changes to the database
        conn.commit()
        
        # Check if the update was successful
        if cursor.rowcount == 0:
            print("No rows were updated.")
        else:
            print(f"{cursor.rowcount} row(s) were updated.")
            
    except Exception as e:
        print(f"An error occurred: {e}")
        conn.rollback()  # Rollback the transaction on error
    finally:
        cursor.close()
        conn.close()
############################################check the location is with in 100 meters ###############################################################################
import threading
import psycopg2
import schedule
import time
import math
from apscheduler.schedulers.background import BackgroundScheduler


def haversine(lat1, lon1, lat2, lon2):
    R = 6371e3  # Radius of the Earth in meters
    phi1, phi2 = math.radians(lat1), math.radians(lat2)
    delta_phi = math.radians(lat2 - lat1)
    delta_lambda = math.radians(lon2 - lon1)
    a = math.sin(delta_phi/2)**2 + math.cos(phi1)*math.cos(phi2)*math.sin(delta_lambda/2)**2
    c = 2*math.atan2(math.sqrt(a), math.sqrt(1-a))
    distance = R * c  # Output distance in meters
    return distance

def fetch_and_compare_locations():
    print('fetch_and_compare_locations')
    conn = connect_db()
    cursor = conn.cursor()
    #cursor.execute("SELECT id, latitude, longitude FROM labormonitoring WHERE isLocation = TRUE")
    cursor.execute('SELECT * FROM public.labormonitoring WHERE "labormonitoring"."isLocation" = %s', (True,))
    target_locations = cursor.fetchall()

    for target in target_locations:
       # print('In target:',target)
        target_id = target [0]
        target_lat = target [2]
        target_lon = target [3]
        cursor.execute('SELECT * FROM public.labormonitoring WHERE "labormonitoring"."isLocation" = %s', (False,))
        for row in cursor.fetchall():
           # print('second loop',row)
            row_id = row [0]
            row_lat = row [2]
            row_lon = row [3]
           # print('row id\t',row_id, '\ttarget id \t',target_id)
            if row_id != target_id:
                distance = haversine(target_lat, target_lon, row_lat, row_lon)
                #print('Distance of the location\t',distance,'\tfrom row id\t',row_id,'\twith targer id\t',target_id,'having targeted lat ', target_lat,'targeted long as',target_lon, 'with row id having row lat',row_lat,'and long as ',row_lon)
                if distance <= 25:
                    print(f"Row {row_id} is within 500 meters of target location {target_id}")
                    update_labormonitoring(row_id,target_id)

    cursor.close()
    conn.close()

def run_periodically():
    print('Run periodically called\n')
    while True:
        print('\n10 sec')
        initilizeLocation()
        fetch_and_compare_locations()
        try:
            jsonMessage= read_sensors()
        except Exception as e:
            print(f"An error occurred: {e}")
        # Wait for 2 minutes or until the stop event is set
        time.sleep(10)
        
        # Handler for graceful shutdown
def signal_handler(signum, frame):
    print("Signal received, shutting down...")
    stop_event.set()
########################################Realtime sensor data value #######################################################################
def home():
    return render_template('index.html')

@app.route('/dashboard')
def dashboard():
    gas_levels = []
    temperature = []
    humidity = []
    conn = connect_db()
    with conn.cursor() as cursor:
        # Let's assume you want to fetch the latest 5 minutes data
        # Considering 'timestamp' is storing Unix timestamp values
        
        locationID = 0  # Or whatever the actual labelID should be

        query = 'SELECT * FROM public."sensorLocationTable" WHERE timestamp >= extract(epoch from now() at time zone \'IST\') - 8000 AND "id" = %s ORDER BY timestamp DESC'
#cursor.execute('SELECT * FROM public."sensorLocationTable" WHERE timestamp >= extract(epoch from now() at time zone \'IST\') - 8000 AND "id" = 0 ORDER BY timestamp DESC')
        cursor.execute(query, (locationID,))

        records = cursor.fetchall()
        for record in records:
            gas_levels.append(record[3])
            temperature.append(record[1])
            humidity.append(record[2])
        data = {"gas_levels" : gas_levels,
                "temperature": temperature,
                "humidity" :humidity
                }
    # Dummy data for demonstration
    # data = {
    #     "gas_levels": [20, 30, 15, 50, 40, 60, 55],
    #     "temperature": [22, 24, 23, 25, 26, 27, 28],
    #     "humidity": [30, 40, 35, 45, 50, 55, 60]
    # }
    return render_template('dashboard.html', data=data)
    

# if __name__ == '__main__':
#     app.run(debug=True)
    #############################################Backgorund run process this is the first program will run##################################################################
#@app.before_first_request
def before_first():
    thread = threading.Thread(target=run_periodically)
    thread.daemon = True  # Daemon threads are abruptly stopped at shutdown
    thread.start()

#################################################################################################################
import signal
import sys
from flask import Flask
from flask import Flask, jsonify, render_template, request, flash
from flask_restful import Api
import psycopg2
   
def signal_handler(signum, frame):
    print("Gracefully shutting down...")
    # Perform any cleanup tasks here
    sys.exit(0)

    

from flask import Flask
from gevent import pywsgi
import ssl
if __name__ == '__main__':
    ssl_context = ssl.SSLContext(ssl.PROTOCOL_TLS_SERVER)
    ssl_context.load_cert_chain('cert.pem', 'key.pem')
    before_first()
    counter = 0 
    app.run(host='0.0.0.0', port=443, ssl_context=ssl_context)
    # http_server = pywsgi.WSGIServer(('0.0.0.0', 443), app, keyfile='key.pem', certfile='cert.pem')
    # http_server.serve_forever()