from utils.auth import hash_password, check_password, create_access_token, check_user
from utils.generators import generate_query, generate_update_query
from utils.serialization import query_output_to_json
from utils.db import get_cursor, get_timestamp
from utils.constants import PORT

from models.queries.base import BaseQuery
from models.queries.update import UpdateQuery


from flask import Flask, request, jsonify
from flask_cors import CORS
import mysql.connector
from typing import List
import json

app = Flask(__name__)
CORS(app)

@app.route("/")
def home():
    return "Hello, World!"

# ================================= AUTH ENDPOINTS =================================
# User registration
@app.route('/auth/register', methods=['POST'])
def register():
    data = request.get_json()
    username = data['username']
    password = data['password']
    email = data['email']

    # Generate a password hash
    pw_hash = hash_password(password)

    try:
        with get_cursor() as cur:
            cur.execute(
                "INSERT INTO users (username, `pass`, email) VALUES (%s, %s, %s)",
                (username, pw_hash, email)
            )
    # If insertion fails due to duplicate username, or other error, return error
    except mysql.connector.IntegrityError as _:
        return jsonify({"error": "Username or email already in use"}), 400
    
    return jsonify({"message":"Registration successful"}), 201

# User login
@app.route('/auth/login', methods=['POST'])
def login():
    data = request.get_json()
    username = data['username']
    password = data['password']

    if not username or not password:
        return jsonify({"error":"Missing credentials"}), 400

    with get_cursor() as cur:
        cur.execute("SELECT pass, email FROM users WHERE username = %s",(username,))
        row = cur.fetchone()

    # If user not found or password does not match, return error
    if not row or not check_password(password, row[0]):
        return jsonify({"error":"Invalid credentials"}), 401
    
    # Generate JWT token with username
    payload = {
      "user": username,
      "email": row[1]
    }
    token = create_access_token(payload)

    # Return the token in the response
    return jsonify({"message":"Login successful", "token": token}), 200

# Get user info
@app.route('/auth/me', methods=['GET'])
def me():
    # Check the authentication of the user
    token = request.headers.get("Authorization")
    user_or_err, error = check_user(token)
    if error:
        return jsonify({"error": user_or_err}), 401

    # Get the username from the token data
    username = user_or_err
    with get_cursor() as cur:
        cur.execute(
          "SELECT username, email FROM users WHERE username = %s",
          (username,)
        )
        row = cur.fetchone()

    if not row:
        return jsonify({"error":"User not found"}), 404

    return jsonify({"username": row[0], "email": row[1]})

# User account deletion
@app.route('/auth/delete_user', methods=['DELETE'])
def delete_account():
    # Check the authentication of the user
    token = request.headers.get("Authorization")
    username, error = check_user(token)
    if error:
        return jsonify({"error": error}), 401

    with get_cursor() as cur:
        try:
            cur.execute("DELETE FROM users WHERE username = %s", (username,))
        except mysql.connector.Error as e:
            print(e)
            return jsonify({"error": "Failed to delete account"}), 500
        
    # Execute the stored procedure to drop the tables that were marked for deletion in the previous step
    with get_cursor() as cur:
        try:
            cur.callproc("process_tables_to_drop")
        except mysql.connector.Error as e:
            print(e)
            return jsonify({"error": "Failed to delete account"}), 500
    
    return jsonify({"message": "Account deleted successfully"}), 200

# =============================== USER DATA ENDPOINTS ===============================
@app.route("/users/save_table", methods=["POST"])
def save_table():
    # Check the authentication of the user
    token = request.headers.get("Authorization")
    username, error = check_user(token)
    if error:
        return jsonify({"error": error}), 401

    data = request.get_json()
    table_name = data.get("table_name")
    query = data.get("query")

    if not table_name or not query:
        return jsonify({"error": "Missing table name or query"}), 400
    
    # Execute the stored procedure to create the table (this checks if the table already exists as well)
    created_at = get_timestamp()
    with get_cursor() as cur:
        try:
            cur.callproc("save_user_table", [username, table_name, created_at, query])
        except mysql.connector.IntegrityError as e:
            print(e)
            return jsonify({"error": e.msg}), 400
        except mysql.connector.Error as e:
            print(e)
            return jsonify({"error": "Failed to save table"}), 500
        
    return jsonify({"message": "Table saved successfully"}), 200

@app.route("/users/delete_table", methods=["POST"])
def drop_table():
    # Check the authentication of the user
    token = request.headers.get("Authorization")
    username, error = check_user(token)
    if error:
        return jsonify({"error": error}), 401

    data = request.get_json()
    # We allow both a single table name and a list of table names, however we convert it to a list regardless for ease of processing
    temp = data.get("table_names")
    if isinstance(temp, str) and temp:
        table_names = [temp]
    elif isinstance(temp, list):
        table_names = temp
    else:
        return jsonify({"error": "Invalid table name format"}), 400
    
    # Execute the query to delete the entries from the user_tables table, which triggers insertion into tables_to_drop
    with get_cursor() as cur:
        try:
            for table_name in table_names:
                if not table_name:
                    return jsonify({"error": "Missing table name"}), 400
                cur.execute("DELETE FROM user_tables WHERE username = %s AND table_name = %s", (username, table_name))
        except mysql.connector.Error as e:
            print(e)
            return jsonify({"error": "Failed to drop table"}), 500
    
    # Execute the stored procedure to drop the tables that were marked for deletion in the previous step
    with get_cursor() as cur:
        try:
            cur.callproc("process_tables_to_drop")
        except mysql.connector.Error as e:
            print(e)
            return jsonify({"error": "Failed to drop table"}), 500
        
    return jsonify({"message": "Table dropped successfully", "success": True, "deleted_tables": table_names}), 200

@app.route("/users/get_tables", methods=["GET"])
def get_tables():
    # Check the authentication of the user
    token = request.headers.get("Authorization")
    username, error = check_user(token)
    if error:
        return jsonify({"error": error}), 401

    rows = []
    with get_cursor() as cur:
        try:
            cur.execute("SELECT table_name, created_at FROM user_tables WHERE username = %s", (username,))
            rows = cur.fetchall()
        except mysql.connector.Error as e:
            print(e)
            return jsonify({"error": "Failed to get tables"}), 500
    if not rows:
        return jsonify({"message": "No tables found"}), 404
    
    tables = [{"table_name": row[0], "created_at": row[1]} for row in rows]
    return jsonify(tables), 200

@app.route("/users/get_table_data", methods=["GET"])
def get_table_data():
    # Check the authentication of the user
    token = request.headers.get("Authorization")
    username, error = check_user(token)
    if error:
        return jsonify({"error": error}), 401

    table_name = request.args.get("table_name")

    if not table_name:
        return jsonify({"error": "Missing table name"}), 400
    
    formatted_table_name = f"u_{username}_{table_name}"
    query = f"SELECT * FROM {formatted_table_name};"
    with get_cursor() as cur:
        try:
            cur.execute(query)
            rows = cur.fetchall()
            column_names = [i[0] for i in cur.description]
        except mysql.connector.Error as e:
            print(e)
            return jsonify({"error": "Failed to get table data"}), 500
    if not rows:
        return jsonify({"message": "No data found"}), 404
    
    return query_output_to_json(rows, column_names, "", 0), 200

@app.route("/users/update_table", methods=["POST"])
def update():
    # Check the authentication of the user
    token = request.headers.get("Authorization")
    username, error = check_user(token)
    if error:
        return jsonify({"error": error}), 401
    data = request.get_json()
    query = UpdateQuery(data, username)
    query_body = generate_update_query(query)
    # with open("logs/update_log.txt", "w") as f:
    #     f.write(query_body)

    if not query_body:
        return jsonify({"error": "Invalid query"}), 400
    
    try:
        with get_cursor() as cursor:
            cursor.execute(query_body)
            result = cursor.rowcount
    except mysql.connector.Error as e:
        print(e)
        return jsonify({"error": "Failed to update table"}), 500

    return jsonify({"message": "Table updated successfully", "success": True, "rows_affected": result}), 200


# ================================= QUERY ENDPOINTS =================================
@app.route("/query", methods=["POST"])
def run_query():
    req: json = request.get_json().get("query", {})
    query: List[BaseQuery] = [BaseQuery(details) for details in req.get("tables", [])]
    query_body = generate_query(query, req.get("options", {}))
    # with open("logs/query_log.txt", "w") as f:
    #     f.write(query_body)

    with get_cursor() as cursor:
        cursor.execute(query_body)
        column_names = [i[0] for i in cursor.description]
        result = cursor.fetchall()

    return query_output_to_json(result, column_names, query_body, len(query)), 200

# @app.route("/test_input", methods=["GET"])
# def test_input():
#     data: List[BaseQuery] = [BaseQuery(details) for details in request.get_json()]
#     with open("logs/input_log.txt", "w") as f:
#         f.write("".join(str(table_query) for table_query in data))

#     return "Hello, world!"


if __name__ == "__main__":
    port = PORT
    app.run(host="0.0.0.0", port=port, threaded=False)