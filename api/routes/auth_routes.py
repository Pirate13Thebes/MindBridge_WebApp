import datetime
import os
import bcrypt
import jwt
from flask import Blueprint, request, jsonify
from db.mysql_db import execute_mysql_query
from utils.validators import validate_username, validate_password, validate_role

auth_bp = Blueprint("auth_bp", __name__)
JWT_SECRET = os.getenv("JWT_SECRET", "jwt-secret-key")

@auth_bp.route("/register", methods=["POST"])
def register():
    """Register a new user account."""
    data = request.get_json() or {}
    username = data.get("username", "").strip()
    password = data.get("password", "")
    role = data.get("role", "patient").strip()
    full_name = data.get("full_name", "").strip()
    
    # Validations
    is_valid, err = validate_username(username)
    if not is_valid:
        return jsonify({"message": err}), 400
        
    is_valid, err = validate_password(password)
    if not is_valid:
        return jsonify({"message": err}), 400
        
    is_valid, err = validate_role(role)
    if not is_valid:
        return jsonify({"message": err}), 400
        
    if not full_name:
        return jsonify({"message": "Full name cannot be empty."}), 400
        
    try:
        # Check uniqueness
        exists = execute_mysql_query("SELECT user_id FROM users WHERE username = %s", (username,), fetchone=True)
        if exists:
            return jsonify({"message": "Username is already taken."}), 400
            
        # Bcrypt hash
        pw_hash = bcrypt.hashpw(password.encode('utf-8'), bcrypt.gensalt()).decode('utf-8')
        
        execute_mysql_query(
            "INSERT INTO users (username, password_hash, role, full_name) VALUES (%s, %s, %s, %s)",
            (username, pw_hash, role, full_name),
            commit=True
        )
        return jsonify({"message": "Account created successfully!"}), 201
    except Exception as e:
        print(f"[Demo Mode Fallback] Registration database failed: {e}")
        from db.mock_db import register_mock_user
        pw_hash = bcrypt.hashpw(password.encode('utf-8'), bcrypt.gensalt()).decode('utf-8')
        res = register_mock_user(username, pw_hash, role, full_name)
        if not res:
            return jsonify({"message": "Username is already taken."}), 400
        return jsonify({"message": "Account created successfully (Offline Demo Mode)!"}), 201

@auth_bp.route("/login", methods=["POST"])
def login():
    """Authenticate user credentials and issue signed JWT."""
    data = request.get_json() or {}
    username = data.get("username", "").strip()
    password = data.get("password", "")
    
    if not username or not password:
        return jsonify({"message": "Username and password are required fields."}), 400
        
    try:
        user = execute_mysql_query(
            "SELECT user_id, username, password_hash, role, full_name FROM users WHERE username = %s",
            (username,),
            fetchone=True
        )
        
        if not user or not bcrypt.checkpw(password.encode('utf-8'), user["password_hash"].encode('utf-8')):
            return jsonify({"message": "Invalid username or password credentials."}), 401
            
        # Create 24hr expiration timestamp using standard timezone-aware utc datetime
        exp_time = datetime.datetime.now(datetime.timezone.utc) + datetime.timedelta(hours=24)
        
        token = jwt.encode({
            "user_id": user["user_id"],
            "username": user["username"],
            "role": user["role"],
            "full_name": user["full_name"],
            "exp": exp_time
        }, JWT_SECRET, algorithm="HS256")
        
        return jsonify({
            "token": token,
            "user": {
                "user_id": user["user_id"],
                "username": user["username"],
                "role": user["role"],
                "full_name": user["full_name"]
            }
        }), 200
    except Exception as e:
        print(f"[Demo Mode Fallback] Login database failed: {e}")
        from db.mock_db import get_mock_user_by_username
        user = get_mock_user_by_username(username)
        if not user or not bcrypt.checkpw(password.encode('utf-8'), user["password_hash"].encode('utf-8')):
            return jsonify({"message": "Invalid username or password credentials."}), 401
            
        exp_time = datetime.datetime.now(datetime.timezone.utc) + datetime.timedelta(hours=24)
        token = jwt.encode({
            "user_id": user["user_id"],
            "username": user["username"],
            "role": user["role"],
            "full_name": user["full_name"],
            "exp": exp_time
        }, JWT_SECRET, algorithm="HS256")
        
        return jsonify({
            "token": token,
            "user": {
                "user_id": user["user_id"],
                "username": user["username"],
                "role": user["role"],
                "full_name": user["full_name"]
            }
        }), 200

