from flask import Flask, request, jsonify
import mysql.connector
from werkzeug.utils import secure_filename
from werkzeug.security import generate_password_hash, check_password_hash
from flask_cors import CORS
import os

app = Flask(__name__)
CORS(app)  # Enable CORS for all routes

UPLOAD_FOLDER = 'C:\\Users\\Asus\\Desktop\\new\\images'  # Define your image upload directory
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER

# Database connection
def get_db_connection():
    return mysql.connector.connect(
        host="localhost",
        user="root",  # Replace with your MySQL username
        password="Sivadeep_45",  # Replace with your MySQL password
        database="autostore"  # Your database name
    )

# Registration route
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

# Login route
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

# Add used car route with image upload
@app.route('/add-used-car', methods=['POST'])
def add_used_car():
    # Get form data
    car_name = request.form.get("carName")
    brand = request.form.get("brand")
    rate = request.form.get("rate")
    car_type = request.form.get("type")
    description = request.form.get("description")
    image = request.files.get("image")

    # Save the image file if uploaded
    image_filename = None
    if image:
        image_filename = secure_filename(image.filename)
        image_path = os.path.join(app.config['UPLOAD_FOLDER'], image_filename)
        image.save(image_path)

    # Database connection and insertion
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute("INSERT INTO used_cars (carName, brand, rate, type, description, imageUrl) VALUES (%s, %s, %s, %s, %s, %s)",
                       (car_name, brand, rate, car_type, description, image_filename))
        conn.commit()
        cursor.close()
        conn.close()
        return jsonify({"message": "Car added successfully!"}), 201
    except Exception as e:
        return jsonify({"error": str(e)}), 500

# Get all used cars route
@app.route('/get-used-cars', methods=['GET'])
def get_used_cars():
    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True)
    cursor.execute("SELECT * FROM used_cars")
    cars = cursor.fetchall()
    cursor.close()
    conn.close()
    return jsonify(cars)

# Delete used car route
@app.route('/delete-used-car/<int:car_id>', methods=['DELETE'])
def delete_used_car(car_id):
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("DELETE FROM used_cars WHERE id = %s", (car_id,))
    conn.commit()
    cursor.close()
    conn.close()
    return jsonify({"message": "Car deleted successfully!"})

if __name__ == '__main__':
    app.run(debug=True)
