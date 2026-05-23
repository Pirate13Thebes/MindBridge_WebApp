import re
from datetime import datetime

def validate_username(username):
    """
    Validate username:
    - Must be 3 to 20 characters long
    - Alphanumeric plus underscores or hyphens only
    """
    if not username:
        return False, "Username cannot be empty."
    if not (3 <= len(username) <= 20):
        return False, "Username must be between 3 and 20 characters long."
    if not re.match(r"^[a-zA-Z0-9_-]+$", username):
        return False, "Username can only contain letters, numbers, underscores, and hyphens."
    return True, ""

def validate_password(password):
    """
    Validate password strength:
    - Minimum length of 6 characters
    """
    if not password:
        return False, "Password cannot be empty."
    if len(password) < 6:
        return False, "Password must be at least 6 characters long."
    return True, ""

def validate_date(date_str):
    """
    Validate if date_str is a valid ISO date string: YYYY-MM-DD
    """
    if not date_str:
        return False, "Date cannot be empty."
    try:
        # Check format and validity
        valid_date = datetime.strptime(date_str, "%Y-%m-%d").date()
        return True, valid_date
    except ValueError:
        return False, "Invalid date format. Please use YYYY-MM-DD."

def validate_role(role):
    """
    Validate if user role is in the allowed ENUM options
    """
    allowed_roles = ["patient", "provider", "admin", "volunteer", "family"]
    if role not in allowed_roles:
        return False, f"Role must be one of: {', '.join(allowed_roles)}"
    return True, ""
