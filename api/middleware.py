import os
from functools import wraps
from flask import request, jsonify, g
import jwt
from dotenv import load_dotenv

load_dotenv()

JWT_SECRET = os.getenv("JWT_SECRET", "jwt-secret-key")

def token_required(f):
    """Decorator to enforce secure routes by checking the JWT token."""
    @wraps(f)
    def decorated(*args, **kwargs):
        token = None
        
        # Check HTTP Authorization header
        if "Authorization" in request.headers:
            auth_header = request.headers["Authorization"]
            if auth_header.startswith("Bearer "):
                token = auth_header.split(" ")[1]
                
        if not token:
            return jsonify({"message": "Access Denied: Missing authentication token."}), 401
            
        try:
            # Decode token
            payload = jwt.decode(token, JWT_SECRET, algorithms=["HS256"])
            g.user = {
                "user_id": payload["user_id"],
                "username": payload["username"],
                "role": payload["role"],
                "full_name": payload["full_name"]
            }
        except jwt.ExpiredSignatureError:
            return jsonify({"message": "Access Denied: Token has expired."}), 401
        except jwt.InvalidTokenError:
            return jsonify({"message": "Access Denied: Invalid authentication token."}), 401
            
        return f(*args, **kwargs)
    return decorated

def admin_required(f):
    """Enforce administrative authorization on routes."""
    @wraps(f)
    def decorated(*args, **kwargs):
        if not hasattr(g, "user") or g.user["role"] != "admin":
            return jsonify({"message": "Access Denied: Administrator role required."}), 403
        return f(*args, **kwargs)
    return decorated

def patient_required(f):
    """Enforce patient authorization on routes."""
    @wraps(f)
    def decorated(*args, **kwargs):
        if not hasattr(g, "user") or g.user["role"] != "patient":
            return jsonify({"message": "Access Denied: Patient role required."}), 403
        return f(*args, **kwargs)
    return decorated

# Updated by fkangira

# Updated by fkangira
