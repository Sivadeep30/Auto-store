from flask import Flask, request, jsonify
from werkzeug.utils import secure_filename
from werkzeug.security import generate_password_hash, check_password_hash
from flask_cors import CORS
import mysql.connector
import os

app = Flask(__name__)
CORS(app)  # Enable CORS for all routes

UPLOAD_FOLDER = './images'  # Define your image upload directory
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER

# Database connection
def get_db_connection():
    return mysql.connector.connect(
        host="localhost",
        user="root",  # Replace with your MySQL username
        password="Sivadeep_45",  # Replace with your MySQL password
        database="autostore"  # Your database name
    )

# User Registration Route
@app.route('/register', methods=['POST'])
def register():
    data = request.get_json()
    name = data['name']
    email = data['email']
    location = data['location']
    password = generate_password_hash(data['password'])

    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute("INSERT INTO users (name, email, location, password) VALUES (%s, %s, %s, %s)",
                       (name, email, location, password))
        conn.commit()
        cursor.close()
        conn.close()
        return jsonify({"message": "User registered successfully!"}), 201
    except mysql.connector.IntegrityError:
        return jsonify({"error": "User already exists with this email!"}), 409

# User Login Route
@app.route('/login', methods=['POST'])
def login():
    data = request.get_json()
    email = data['email']
    password = data['password']

    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True)
    cursor.execute("SELECT * FROM users WHERE email = %s", (email,))
    user = cursor.fetchone()
    cursor.close()
    conn.close()

    if user and check_password_hash(user['password'], password):
        return jsonify({"message": "Login successful!", "user": {"id": user['id'], "name": user['name'], "email": user['email']}})
    else:
        return jsonify({"error": "Invalid email or password!"}), 401

# Admin Login Route
@app.route('/admin-login', methods=['POST'])
def admin_login():
    data = request.get_json()
    admin_id = "admin"  # Replace with your predefined admin ID
    admin_password = "admin_pass"  # Replace with your predefined admin password
    if data['id'] == admin_id and data['password'] == admin_password:
        return jsonify({"message": "Admin login successful!"}), 200
    else:
        return jsonify({"error": "Invalid admin credentials!"}), 401

# Add New Car (Admin)
@app.route('/add-car', methods=['POST'])
def add_car():
    car_name = request.form.get("carName")
    brand = request.form.get("brand")
    rate = request.form.get("rate")
    car_type = request.form.get("type")
    description = request.form.get("description")
    image = request.files.get("imageUrl")

    print(car_name,car_type,rate, car_type, description, image)

    image_filename = None
    if image:
        image_filename = secure_filename(image.filename)
        image_path = os.path.join(app.config['UPLOAD_FOLDER'], image_filename)
        image.save(image_path)

    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute("INSERT INTO cars (car_name, brand, rate, type, description, image_url) VALUES (%s, %s, %s, %s, %s, %s)",
                       (car_name, brand, rate, car_type, description, image_filename))
        conn.commit()
        cursor.close()
        conn.close()
        return jsonify({"message": "Car added successfully!"}), 201
    except Exception as e:
        print("Error adding car:", str(e))
        return jsonify({"error": str(e)}), 500

@app.route('/get_cars', methods=['GET'])
def get_cars():
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute("SELECT id, car_name, brand, rate, type, image_url FROM cars")
        cars = cursor.fetchall()
        cursor.close()
        conn.close()

        # Format the data as a list of dictionaries
        car_list = []
        for car in cars:
            car_list.append({
                "id": car[0],
                "carName": car[1],
                "brand": car[2],
                "rate": car[3],
                "type": car[4],
                "imageUrl": car[5]  # Make sure imageUrl is correctly referenced here
            })

        return jsonify(car_list), 200
    except Exception as e:
        print("Error fetching cars:", str(e))
        return jsonify({"error": str(e)}), 500

# Update Car Details (Admin)
@app.route('/update_car/<int:car_id>', methods=['PUT'])
def update_car(car_id):
    data = request.get_json()
    car_name = data.get("carName")
    brand = data.get("brand")
    rate = data.get("rate")
    car_type = data.get("type")
    description = data.get("description")

    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute("""
            UPDATE cars
            SET car_name = %s, brand = %s, rate = %s, type = %s, description = %s
            WHERE id = %s
        """, (car_name, brand, rate, car_type, description, car_id))
        conn.commit()
        cursor.close()
        conn.close()
        return jsonify({"message": "Car updated successfully!"}), 200
    except Exception as e:
        print("Error updating car:", str(e))
        return jsonify({"error": str(e)}), 500

# Delete Car (Admin)
@app.route('/delete_car/<int:car_id>', methods=['DELETE'])
def delete_car(car_id):
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute("DELETE FROM cars WHERE id = %s", (car_id,))
        conn.commit()
        cursor.close()
        conn.close()
        return jsonify({"message": "Car deleted successfully!"}), 200
    except Exception as e:
        print("Error deleting car:", str(e))
        return jsonify({"error": str(e)}), 500

# Add Used Car (with Image Upload)
@app.route('/add-used-car', methods=['POST'])
def add_used_car():
    car_name = request.form.get("carName")
    brand = request.form.get("brand")
    rate = request.form.get("rate")
    car_type = request.form.get("type")
    description = request.form.get("description")
    image = request.files.get("image")

    image_filename = None
    if image:
        image_filename = secure_filename(image.filename)
        image_path = os.path.join(app.config['UPLOAD_FOLDER'], image_filename)
        image.save(image_path)

    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute("INSERT INTO used_cars (carName, brand, rate, type, description, imageUrl) VALUES (%s, %s, %s, %s, %s, %s)",
                       (car_name, brand, rate, car_type, description, image_filename))
        conn.commit()
        cursor.close()
        conn.close()
        return jsonify({"message": "Used car added successfully!"}), 201
    except Exception as e:
        return jsonify({"error": str(e)}), 500

# Get All Used Cars
@app.route('/get-used-cars', methods=['GET'])
def get_used_cars():
    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True)
    cursor.execute("SELECT * FROM used_cars")
    cars = cursor.fetchall()
    cursor.close()
    conn.close()
    return jsonify(cars), 200

# Delete Used Car by ID
@app.route('/delete-used-car/<int:car_id>', methods=['DELETE'])
def delete_used_car(car_id):
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("DELETE FROM used_cars WHERE id = %s", (car_id,))
    conn.commit()
    cursor.close()
    conn.close()
    return jsonify({"message": "Used car deleted successfully!"}), 200

if __name__ == '__main__':
    app.run(debug=True)
