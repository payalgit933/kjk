# eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJmcmVzaCI6ZmFsc2UsImlhdCI6MTc1MTk5OTgwNSwianRpIjoiZjcyYmJkMWEtZmE0ZS00NWI1LTgxNmQtMjEzYWZlZDhhOWY0IiwidHlwZSI6ImFjY2VzcyIsInN1YiI6eyJpZCI6MSwicm9sZSI6ImN1c3RvbWVyIn0sIm5iZiI6MTc1MTk5OTgwNSwiY3NyZiI6ImEwZDgzNzI5LWIxNDktNDI4ZC1iMjRlLWE2ZGIxNWY2ODNlNyIsImV4cCI6MTc1MjA4NjIwNX0.s3mA9k2h85gI-LadhFNj8DYBA5ijXS1OYozYly9zIwc
from flask import Flask, request, jsonify
from flask_cors import CORS
import mysql.connector
from werkzeug.security import generate_password_hash, check_password_hash
from flask_jwt_extended import (
    JWTManager, create_access_token, jwt_required,
    get_jwt_identity, get_jwt
)
import datetime

app = Flask(__name__)
CORS(app)

# Config
app.config['JWT_SECRET_KEY'] = 'your-secret-key'  # Replace with a strong key in production
jwt = JWTManager(app)

# Connect to MySQL (XAMPP or localhost)
db = mysql.connector.connect(
    host="localhost",
    user="root",
    password="",  # your MySQL password
    database="kirana_store"
)
cursor = db.cursor(dictionary=True)

# ------------------- AUTH ROUTES ------------------- #

# Register
@app.route('/register', methods=['POST'])
def register():
    data = request.get_json()
    name = data['name']
    email = data['email']
    password = generate_password_hash(data['password'])

    try:
        cursor.execute("INSERT INTO users (name, email, password) VALUES (%s, %s, %s)", 
                       (name, email, password))
        db.commit()
        return jsonify({"message": "User registered successfully"}), 201
    except mysql.connector.errors.IntegrityError:
        return jsonify({"error": "Email already registered"}), 409

# Login
@app.route('/login', methods=['POST'])
def login():
    data = request.get_json()
    email = data['email']
    password = data['password']

    cursor.execute("SELECT * FROM users WHERE email = %s", (email,))
    user = cursor.fetchone()

    print("User from DB:", user)

    if user and check_password_hash(user['password'], password):
        user_id = str(user['id'])  # ✅ convert to string
        user_role = user['role'].strip().lower()  # ✅ clean role

        access_token = create_access_token(
            identity=user_id,  # ✅ subject must be string
            additional_claims={"role": user_role},  # ✅ role moved here
            expires_delta=datetime.timedelta(days=1)
        )

        return jsonify({"token": access_token}), 200
    else:
        return jsonify({"error": "Invalid credentials"}), 401



# ------------------- PRODUCT ROUTES ------------------- #

# Add Product (Shop Owner only)
@app.route('/products', methods=['POST'])
@jwt_required()
def add_product():
    claims = get_jwt()
    print("JWT claims:", claims)  # 👈 add this

    if claims['role'] != 'shop_owner':
        return jsonify({"error": "Unauthorized"}), 403

    data = request.get_json()
    name = data['name']
    category = data['category']
    price = data['price']
    stock = data['stock']
    image_url = data['image_url']

    cursor.execute("INSERT INTO products (name, category, price, stock, image_url) VALUES (%s, %s, %s, %s, %s)",
                   (name, category, price, stock, image_url))
    db.commit()
    return jsonify({"message": "Product added successfully"}), 201

# Get All Products (Public)
@app.route('/products', methods=['GET'])
def get_products():
    cursor.execute("SELECT * FROM products")
    products = cursor.fetchall()
    return jsonify(products), 200

# Update Product (Shop Owner only)
@app.route('/products/<int:product_id>', methods=['PUT'])
@jwt_required()
def update_product(product_id):
    claims = get_jwt()
    if claims['role'] != 'shop_owner':
        return jsonify({"error": "Unauthorized"}), 403

    data = request.get_json()
    cursor.execute("""
        UPDATE products SET name=%s, category=%s, price=%s, stock=%s, image_url=%s WHERE id=%s
    """, (data['name'], data['category'], data['price'], data['stock'], data['image_url'], product_id))
    db.commit()
    return jsonify({"message": "Product updated"}), 200

# Delete Product (Shop Owner only)
@app.route('/products/<int:product_id>', methods=['DELETE'])
@jwt_required()
def delete_product(product_id):
    claims = get_jwt()
    if claims['role'] != 'shop_owner':
        return jsonify({"error": "Unauthorized"}), 403

    cursor.execute("DELETE FROM products WHERE id = %s", (product_id,))
    db.commit()
    return jsonify({"message": "Product deleted"}), 200

# Place order
@app.route('/place-order', methods=['POST'])
@jwt_required()
def place_order():
    claims = get_jwt()
    if claims['role'] != 'customer':
        return jsonify({"error": "Only customers can place orders"}), 403

    user_id = get_jwt_identity()  # This is a string
    data = request.get_json()
    items = data['items']  # List of: {product_id, quantity}

    total_amount = 0

    # 1. Calculate total and update stock
    for item in items:
        cursor.execute("SELECT * FROM products WHERE id = %s", (item['product_id'],))
        product = cursor.fetchone()

        if not product:
            return jsonify({"error": f"Product {item['product_id']} not found"}), 404
        if product['stock'] < item['quantity']:
            return jsonify({"error": f"Insufficient stock for {product['name']}"}), 400

        total_amount += item['quantity'] * float(product['price'])

    # 2. Insert order
    cursor.execute("INSERT INTO orders (user_id, total_amount) VALUES (%s, %s)", (user_id, total_amount))
    db.commit()
    order_id = cursor.lastrowid

    # 3. Insert order items & update stock
    for item in items:
        cursor.execute("SELECT price FROM products WHERE id = %s", (item['product_id'],))
        product = cursor.fetchone()
        cursor.execute("INSERT INTO order_items (order_id, product_id, quantity, price) VALUES (%s, %s, %s, %s)",
                       (order_id, item['product_id'], item['quantity'], product['price']))
        cursor.execute("UPDATE products SET stock = stock - %s WHERE id = %s", (item['quantity'], item['product_id']))

    db.commit()

    return jsonify({"message": "Order placed successfully", "order_id": order_id}), 201
# View Their Own Orders
@app.route('/my-orders', methods=['GET'])
@jwt_required()
def get_my_orders():
    claims = get_jwt()
    if claims['role'] != 'customer':
        return jsonify({"error": "Only customers can view their orders"}), 403

    user_id = get_jwt_identity()

    # Get orders by user
    cursor.execute("SELECT * FROM orders WHERE user_id = %s", (user_id,))
    orders = cursor.fetchall()

    result = []
    for order in orders:
        cursor.execute("""
            SELECT oi.product_id, p.name, oi.quantity, oi.price
            FROM order_items oi
            JOIN products p ON oi.product_id = p.id
            WHERE oi.order_id = %s
        """, (order['id'],))
        items = cursor.fetchall()
        result.append({
            "order_id": order['id'],
            "order_date": order['order_date'].strftime('%Y-%m-%d %H:%M'),
            "total_amount": float(order['total_amount']),
            "items": items
        })

    return jsonify(result)
# View All Orders (All Customers)
@app.route('/all-orders', methods=['GET'])
@jwt_required()
def get_all_orders():
    claims = get_jwt()
    if claims['role'] != 'shop_owner':
        return jsonify({"error": "Only shop owners can view all orders"}), 403

    cursor.execute("""
        SELECT o.id AS order_id, o.order_date, o.total_amount,
               u.name AS customer_name, u.email AS customer_email
        FROM orders o
        JOIN users u ON o.user_id = u.id
        ORDER BY o.order_date DESC
    """)
    orders = cursor.fetchall()

    result = []
    for order in orders:
        cursor.execute("""
            SELECT oi.product_id, p.name, oi.quantity, oi.price
            FROM order_items oi
            JOIN products p ON oi.product_id = p.id
            WHERE oi.order_id = %s
        """, (order['order_id'],))
        items = cursor.fetchall()

        result.append({
            "order_id": order['order_id'],
            "order_date": order['order_date'].strftime('%Y-%m-%d %H:%M'),
            "total_amount": float(order['total_amount']),
            "customer_name": order['customer_name'],
            "customer_email": order['customer_email'],
            "items": items
        })

    return jsonify(result)


if __name__ == "__main__":
    app.run(debug=True)
