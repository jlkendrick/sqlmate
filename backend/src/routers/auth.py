from utils.auth import create_access_token, check_user, hash_password, check_password, get_token
from utils.db import get_cursor
from models.http import StatusResponse

from typing import Any, Optional
from fastapi import APIRouter, Header
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
@router.post('/register')
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
class LoginRequest(BaseModel):
    username: str
    password: str
class LoginResponse(BaseModel):
    status: StatusResponse
    token: str | None = None
@router.post('/login')
def login(req: LoginRequest) -> LoginResponse:
    username = req.username
    password = req.password

    if not username or not password:
        return LoginResponse(
			status=StatusResponse(
				status="warning",
				message="Username and password are required"
			)
		)

    with get_cursor("sqlmate") as cur:
        cur.execute("SELECT password, email FROM users WHERE username = %s",(username,))
        row: Any = cur.fetchone()

    # If user not found or password does not match, return error
    if not row or not check_password(password, row[0]):
        return LoginResponse(
			status=StatusResponse(
				status="error",
				message="Invalid username or password"
			)
		)
    
    # Generate JWT token with username
    payload = {
      "user": username,
      "email": row[1]
    }
    token = create_access_token(payload)

    # Return the token in the response
    return LoginResponse(
		status=StatusResponse(
			status="success",
			message="Login successful"
		),
		token=token
	)

# Get user info
class UserInfoResponse(BaseModel):
    status: StatusResponse
    username: str | None = None
    email: str | None = None
@router.get('/me')
def me(authorization: Optional[str] = Header(None)) -> UserInfoResponse:
    # Check the authentication of the user
    token = get_token(authorization)
    user_or_err, error = check_user(token)
    if error:
        return UserInfoResponse(
            status=StatusResponse(
				status="error",
				message=error
			),
            username=None,
			email=None
		)

    # Get the username from the token data
    username = user_or_err
    with get_cursor("sqlmate") as cur:
        cur.execute(
          "SELECT username, email FROM users WHERE username = %s",
          (username,)
        )
        row: Any = cur.fetchone()

    if not row:
        return UserInfoResponse(
            status=StatusResponse(
				status="error",
				message="User not found"
			),
			username=None,
			email=None
		)

    return UserInfoResponse(
		status=StatusResponse(
			status="success",
			message="User info retrieved successfully"
		),
		username=row[0],
		email=row[1]
	)

# User account deletion
class DeleteAccountResponse(BaseModel):
    status: StatusResponse
@router.get('/delete_user')
def delete_account(authorization: Optional[str] = Header(None)) -> DeleteAccountResponse:
    # Check the authentication of the user
    token = get_token(authorization)
    username, error = check_user(token)
    if error:
        return DeleteAccountResponse(
			status=StatusResponse(
				status="error",
				message=error
			)
		)

    with get_cursor("sqlmate") as cur:
        try:
            cur.execute("DELETE FROM users WHERE username = %s", (username,))
        except mysql.connector.Error as e:
            print(e)
            return DeleteAccountResponse(
				status=StatusResponse(
					status="error",
					message="Failed to delete account"
				)
			)
        
    # Execute the stored procedure to drop the tables that were marked for deletion in the previous step
    with get_cursor() as cur:
        try:
            cur.callproc("process_tables_to_drop")
        except mysql.connector.Error as e:
            print(e)
            return DeleteAccountResponse(
				status=StatusResponse(
					status="error",
					message="Failed to process tables for deletion"
				)
			)
    
    return DeleteAccountResponse(
		status=StatusResponse(
			status="success",
			message="Account deleted successfully"
		)
	)