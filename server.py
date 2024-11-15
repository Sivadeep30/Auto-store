from flask import Flask, request, jsonify, session
from werkzeug.utils import secure_filename
from werkzeug.security import generate_password_hash, check_password_hash
from flask_cors import CORS
import mysql.connector
import os
from flask_session import Session

app = Flask(__name__)
CORS(app, supports_credentials=True)  # Enable CORS and support credentials

# Configurations for session
app.config['SECRET_KEY'] = 'your_secret_key_here'  # Use a strong secret key for sessions
app.config['SESSION_TYPE'] = 'filesystem'
Session(app)  # Set up session management

UPLOAD_FOLDER = './images'
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER

# Database connection
def get_db_connection():
    return mysql.connector.connect(
        host="localhost",
        user="root",
        password="Sivadeep_45",
        database="autostore"
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
        session['user_id'] = user['id']
        session['user_email'] = user['email']
        print( session['user_email'])
        session['is_admin'] = False
        return jsonify({"message": "Login successful!", "user": {"id": user['id'], "name": user['name'], "email": user['email']}})
    else:
        return jsonify({"error": "Invalid email or password!"}), 401


# Admin Login Route
@app.route('/admin-login', methods=['POST'])
def admin_login():
    data = request.get_json()
    admin_id = "admin"
    admin_password = "admin_pass"
    if data['id'] == admin_id and data['password'] == admin_password:
        session['user_id'] = admin_id
        session['is_admin'] = True
        return jsonify({"message": "Admin login successful!"}), 200
    else:
        return jsonify({"error": "Invalid admin credentials!"}), 401

@app.route('/profile', methods=['GET'])
def profile():
    email = request.args.get('email')
    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True)
    cursor.execute("SELECT * FROM users WHERE email = %s", (email,))
    user = cursor.fetchone()
    cursor.close()
    conn.close()

    if user:
        return jsonify({"profile": {"name": user['name'], "email": user['email'], "location": user['location']}})
    else:
        return jsonify({"error": "User not found"}), 404


# Logout Route
@app.route('/logout', methods=['POST'])
def logout():
    session.clear()
    return jsonify({"message": "Logged out successfully!"}), 200

# Admin Login Route
@app.route('/admin-login', methods=['POST'], endpoint='admin_login_post')
def admin_login_post():
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

    # Retrieve user email from session
    user_email = request.form.get("user_email")
    print(user_email)

    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute(
            "INSERT INTO used_cars (carName, brand, rate, type, description, imageUrl, user_email) VALUES (%s, %s, %s, %s, %s, %s, %s)",
            (car_name, brand, rate, car_type, description, image_filename, user_email)
        )
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

    # Get the logged-in user's email from session
    user_email = request.args.get('email')

    # Add the login status and ownership check to each car
    for car in cars:
        if user_email and car['user_email'] == user_email:  # Check if the user is the owner
            car['is_owner'] = True  # Show delete button if the user is the owner
        else:
            car['is_owner'] = False  # Hide delete button if the user is not the owner
    print(car)
    response = {
        "cars": cars,
        "loggedIn": bool(user_email)  # Check if the user is logged in
    }
    
    return jsonify(response), 200


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

# Get Cars by Brand
@app.route('/cars/<string:brand>', methods=['GET'])
def get_cars_by_brand(brand):
    try:
        conn = get_db_connection()
        cursor = conn.cursor(dictionary=True)
        cursor.execute("SELECT * FROM cars WHERE brand = %s", (brand,))
        cars = cursor.fetchall()
        cursor.close()
        conn.close()

        if not cars:
            return jsonify({"error": f"No cars found for brand {brand}"}), 404

        return jsonify(cars), 200
    except Exception as e:
        print("Error fetching cars by brand:", str(e))
        return jsonify({"error": str(e)}), 500

@app.route('/purchase', methods=['POST'])
def handle_purchase():
    try:
        # Get purchase details from the request body
        data = request.json
        car_name = data.get('carName')
        name = data.get('name')
        email = data.get('email')
        phone = data.get('phone')
        location = data.get('location')

        if not all([car_name, name, email, phone, location]):
            return jsonify({"error": "All fields are required!"}), 400

        # SQL query to insert purchase details into the 'purchases' table
        query = """
            INSERT INTO purchases (car_name, name, email, phone, location)
            VALUES (%s, %s, %s, %s, %s)
        """

        connection = get_db_connection()
        cursor = connection.cursor()

        # Execute the query and commit the changes to the database
        cursor.execute(query, (car_name, name, email, phone, location))
        connection.commit()

        return jsonify({"message": "Purchase successful!"}), 200

    except Exception as e:
        print(f"Error: {e}")
        return jsonify({"error": "An error occurred while processing the purchase"}), 500
    finally:
        cursor.close()
        connection.close()

@app.route('/admin/purchases', methods=['GET'])
def get_purchases():
    try:
        conn = get_db_connection()
        cursor = conn.cursor(dictionary=True)
        
        # Fetch the latest 5 purchase records
        cursor.execute("SELECT * FROM purchases ORDER BY id DESC LIMIT 5")
        purchases = cursor.fetchall()
        
        cursor.close()
        conn.close()
        
        return jsonify(purchases), 200
    except Exception as e:
        print(f"Error fetching purchases: {e}")
        return jsonify({"error": "An error occurred while fetching purchases"}), 500

#@app.route('/admin/purchases', methods=['GET'])
#def get_purchases():
 #   try:
  #      conn = get_db_connection()
   #     cursor = conn.cursor(dictionary=True)
        
        # Execute a query to fetch all purchase records
    #    cursor.execute("SELECT * FROM purchases")
     #   purchases = cursor.fetchall()
        
      #  cursor.close()
       # conn.close()
        
        # Format the data to return in JSON format
        #purchase_list = [
         #   {
          #      "id": purchase["id"],
           #     "car_name": purchase["car_name"],
            #    "name": purchase["name"],
             #   "email": purchase["email"],
              #  "phone": purchase["phone"],
               # "location": purchase["location"],
                #"purchase_date": purchase["purchase_date"].strftime('%Y-%m-%d %H:%M:%S')
            #}
            #for purchase in purchases
        #]
        
        #return jsonify(purchase_list), 200
    
    #except Exception as e:
#        print("Error fetching purchases:", str(e))
 #   return jsonify({"error": str(e)}), 500

# Submit Feedback Route
@app.route('/submit-feedback', methods=['POST'])
def submit_feedback():
    data = request.get_json()
    feedback_text = data.get('feedback_text')

    if not feedback_text:
        return jsonify({"error": "Feedback text is required!"}), 400

    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True)
    cursor.execute("INSERT INTO feedback (feedback_text) VALUES (%s)", (feedback_text,))
    conn.commit()
    cursor.close()
    conn.close()

    return jsonify({"message": "Feedback submitted successfully!"}), 200

# Get Feedback Route
@app.route('/feedback', methods=['GET'])
def get_feedback():
    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True)
    cursor.execute("SELECT * FROM feedback ORDER BY created_at DESC")
    feedbacks = cursor.fetchall()
    cursor.close()
    conn.close()

    return jsonify(feedbacks), 200

if __name__ == '__main__':
    app.run(debug=True)
