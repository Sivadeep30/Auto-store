from flask import Flask, request, jsonify
import mysql.connector
from werkzeug.security import generate_password_hash, check_password_hash
from flask_cors import CORS

app = Flask(__name__)
CORS(app)  # Enable CORS for all routes




# Database connection
def get_db_connection():
    return mysql.connector.connect(
        host="localhost",
        user="root",  # Replace with your MySQL username
        password="Sivadeep_45",  # Replace with your MySQL password
        database="autostore"  # Updated to 'autostore' as per your database
    )

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

if __name__ == '__main__':
    app.run(debug=True)
