from utils.auth import create_access_token, check_user, hash_password, check_password
from utils.db import get_cursor
from models.http.response import StatusResponse

from fastapi import APIRouter
from pydantic import BaseModel
import mysql.connector

router = APIRouter()

# ================================= AUTH ENDPOINTS =================================

# User registration
class RegisterRequest(BaseModel):
	username: str
	password: str
	email: str
class RegisterResponse(BaseModel):
    status: StatusResponse
@router.post('/auth/register')
def register(req: RegisterRequest) -> RegisterResponse:
    username = req.username
    password = req.password
    email = req.email

    # Generate a password hash
    pw_hash = hash_password(password)

    try:
        with get_cursor("sqlmate") as cur:
            cur.execute(
                "INSERT INTO users (username, password, email) VALUES (%s, %s, %s)",
                (username, pw_hash, email)
            )
            
    # If insertion fails due to duplicate username, or other error, return error
    except mysql.connector.IntegrityError as _:
        return RegisterResponse(
			status=StatusResponse(
				status="error",
				message="Username already exists"
			)
		)
    
    except mysql.connector.Error as e:
        print(e)
        return RegisterResponse(
			status=StatusResponse(
				status="error",
				message="Failed to register user"
			)
		)
    
    return RegisterResponse(
		status=StatusResponse(
			status="success",
			message="User registered successfully"
		)
	)

# User login
@router.post('/auth/login')
def login():
    data = request.get_json()
    username = data['username']
    password = data['password']

    if not username or not password:
        return jsonify({"error":"Missing credentials"}), 400

    with get_cursor("sqlmate") as cur:
        cur.execute("SELECT password, email FROM users WHERE username = %s",(username,))
        row: Any = cur.fetchone()

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
@router.get('/auth/me')
def me():
    # Check the authentication of the user
    token = request.headers.get("Authorization")
    user_or_err, error = check_user(token)
    if error:
        return jsonify({"error": user_or_err}), 401

    # Get the username from the token data
    username = user_or_err
    with get_cursor("sqlmate") as cur:
        cur.execute(
          "SELECT username, email FROM users WHERE username = %s",
          (username,)
        )
        row: Any = cur.fetchone()

    if not row:
        return jsonify({"error":"User not found"}), 404

    return jsonify({"username": row[0], "email": row[1]})

# User account deletion
@router.get('/auth/delete_user')
def delete_account():
    # Check the authentication of the user
    token = request.headers.get("Authorization")
    username, error = check_user(token)
    if error:
        return jsonify({"error": error}), 401

    with get_cursor("sqlmate") as cur:
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