from flask import Flask, request, jsonify,render_template
from pymongo import MongoClient
from datetime import datetime
from flask_cors import CORS

app = Flask(__name__)
CORS(app)

# MongoDB client setup (replace with your actual MongoDB URI)
client = MongoClient('mongodb+srv://hematejaswi:1234567890@sparklesquad.kxlgr.mongodb.net/')
db = client['Fake_product']
collection = db['products']

@app.route("/")
def index():
    return render_template("form.html")

@app.route('/submit', methods=['POST'])
def insert_data():
    record_id = request.form.get('product_id')
    product_name = request.form['product_name']
    expiry_date_str = request.form.get('expiry_date')  # Expected format: 'YYYY-MM-DD'
    
    if not record_id or not expiry_date_str:
        return jsonify({"error": "Missing product_id or expiry_date parameter"}), 400
    
    try:
        expiry_date = datetime.strptime(expiry_date_str, '%Y-%m-%d')
    except ValueError:
        return jsonify({"error": "Invalid expiry_date format. Use 'YYYY-MM-DD'."}), 400
    
    # Check if the product_id already exists in the database
    existing_product = collection.find_one({"id": record_id})
    if existing_product:
        return render_template("form.html",message= f"Product with ID {record_id} already exists."), 400
    
    # Prepare data to be inserted into MongoDB
    record = {
        "id": record_id,
        "expiry_date": expiry_date,
        "name": product_name
    }

    try:
        collection.insert_one(record)
        return render_template("form.html", message="Product added successfully")
    except Exception as e:
        return jsonify({"error": str(e)}), 500
    @app.route('/verify', methods=['GET'])
def verify_product():
    product_id = request.args.get('id')
    
    if not product_id:
        return jsonify({"error": "Product ID is required"}), 400
    
    # Check if the product_id exists in the database
    product = collection.find_one({"id": product_id})
    
    if not product:
        return jsonify({"status": 1, "message": "Fake product"}), 404  # Product doesn't exist
    
    # Check expiry date
    current_date = datetime.now()
    expiry_date = product.get('expiry_date')

    if not expiry_date:
        return jsonify({"error": "No expiry date found for this product"}), 400
    
    # Convert expiry_date string to datetime object if it's in string format
    if isinstance(expiry_date, str):
        try:
            expiry_date = datetime.strptime(expiry_date, "%Y-%m-%d")  # Adjust format if necessary
        except ValueError:
            return jsonify({"error": "Invalid expiry date format"}), 400
    
    # Check if the product has expired
    if current_date > expiry_date:
        return jsonify({"status": 2, "message": "Product expired"}), 200  # Product expired
    else:
        return jsonify({"status": 3, "message": "Product valid"}), 200  # Product valid


if __name__ == '__main__':
    app.run(debug=True)
