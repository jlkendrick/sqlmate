from utils.auth import create_access_token, check_user, hash_password, check_password, get_token
from utils.db import get_cursor
from classes.http import StatusResponse

from typing import Any, Optional
from fastapi import APIRouter, Header, Response, status
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
    details: StatusResponse
@router.post('/register', status_code=status.HTTP_201_CREATED)
def register(req: RegisterRequest, response: Response) -> RegisterResponse:
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
        response.status_code = status.HTTP_409_CONFLICT
        return RegisterResponse(
			details=StatusResponse(
				status="error",
				message="Username already exists",
                code=status.HTTP_409_CONFLICT
			)
		)
    
    except mysql.connector.Error as e:
        print(e)
        response.status_code = status.HTTP_500_INTERNAL_SERVER_ERROR
        return RegisterResponse(
			details=StatusResponse(
				status="error",
				message="Failed to register user",
                code=status.HTTP_500_INTERNAL_SERVER_ERROR
			)
		)
    
    return RegisterResponse(
		details=StatusResponse(
			status="success",
			message="User registered successfully",
            code=status.HTTP_201_CREATED
		)
	)

# User login
class LoginRequest(BaseModel):
    username: str
    password: str
class LoginResponse(BaseModel):
    details: StatusResponse
    token: str | None = None
@router.post('/login', response_model=LoginResponse, status_code=status.HTTP_200_OK)
def login(req: LoginRequest, response: Response) -> LoginResponse:
    username = req.username
    password = req.password

    if not username or not password:
        response.status_code = status.HTTP_400_BAD_REQUEST
        return LoginResponse(
			details=StatusResponse(
				status="warning",
				message="Username and password are required",
                code=status.HTTP_400_BAD_REQUEST
			)
		)

    with get_cursor("sqlmate") as cur:
        cur.execute("SELECT id, password, email FROM users WHERE username = %s",(username,))
        row: Any = cur.fetchone()

    # If user not found or password does not match, return error
    if not row or not check_password(password, row[1]):
        response.status_code = status.HTTP_401_UNAUTHORIZED
        return LoginResponse(
			details=StatusResponse(
				status="error",
				message="Invalid username or password",
                code=status.HTTP_401_UNAUTHORIZED
			)
		)
    
    # Generate JWT token with username
    payload = {
        "id": row[0],
        "username": username,
        "email": row[2]
    }
    token = create_access_token(payload)

    # Return the token in the response
    return LoginResponse(
		details=StatusResponse(
			status="success",
			message="Login successful",
            code=status.HTTP_200_OK
		),
		token=token
	)

# Get user info
class UserInfoResponse(BaseModel):
    details: StatusResponse
    username: str | None = None
    email: str | None = None
@router.get('/me', response_model=UserInfoResponse, status_code=status.HTTP_200_OK)
def me(response: Response, authorization: Optional[str] = Header(None)) -> UserInfoResponse:
    # Check the authentication of the user
    user_id, username, error = check_user(authorization)
    if error:
        response.status_code = status.HTTP_401_UNAUTHORIZED
        return UserInfoResponse(
            details=StatusResponse(
				status="error",
				message=error,
                code=status.HTTP_401_UNAUTHORIZED
			),
            username=None,
			email=None
		)

    # Get the username from the token data
    with get_cursor("sqlmate") as cur:
        cur.execute(
          "SELECT username, email FROM users WHERE id = %s",
          (user_id,)
        )
        row: Any = cur.fetchone()

    if not row:
        response.status_code = status.HTTP_404_NOT_FOUND
        return UserInfoResponse(
            details=StatusResponse(
				status="error",
				message="User not found",
                code=status.HTTP_404_NOT_FOUND
			),
			username=None,
			email=None
		)

    return UserInfoResponse(
		details=StatusResponse(
			status="success",
			message="User info retrieved successfully",
            code=status.HTTP_200_OK
		),
		username=row[0],
		email=row[1]
	)

# User account deletion
class DeleteAccountResponse(BaseModel):
    details: StatusResponse
@router.delete('/delete_user')
def delete_account(authorization: Optional[str] = Header(None)) -> DeleteAccountResponse:
    # Check the authentication of the user
    token = get_token(authorization)
    user_id, username, error = check_user(token)
    if error:
        return DeleteAccountResponse(
			details=StatusResponse(
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
				details=StatusResponse(
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
				details=StatusResponse(
					status="error",
					message="Failed to process tables for deletion"
				)
			)
    
    return DeleteAccountResponse(
		details=StatusResponse(
			status="success",
			message="Account deleted successfully"
		)
	)