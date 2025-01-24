from flask import Flask, request, jsonify,render_template
from pymongo import MongoClient
from datetime import datetime

app = Flask(__name__)

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
        return jsonify({"message": "Fake product"}), 404  # Product doesn't exist
    
    # Check expiry date
    current_date = datetime.now()
    expiry_date = product.get('expiry_date')

    if not expiry_date:
        return jsonify({"error": "No expiry date found for this product"}), 400
    
    if current_date > expiry_date:
        return jsonify({
            "message": f"Product {product_id} is expired. Expiry Date: {expiry_date.isoformat()}"
        }), 200
    else:
        return jsonify({
            "message": f"Product {product_id} is valid. Expiry Date: {expiry_date.isoformat()}"
        }), 200

if __name__ == '__main__':
    app.run(debug=True)
