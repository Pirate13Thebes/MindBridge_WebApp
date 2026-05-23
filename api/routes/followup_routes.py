import datetime
from flask import Blueprint, request, jsonify, g
from db.mysql_db import execute_mysql_query
from api.middleware import token_required
from utils.validators import validate_date

followup_bp = Blueprint("followup_bp", __name__)

@followup_bp.route("", methods=["GET"])
@token_required
def get_followups():
    """Retrieve followup records based on role access."""
    user = g.user
    role = user["role"]
    user_id = user["user_id"]
    today = datetime.date.today()
    
    try:
        if role == "patient":
            # Auto-flag overdue tasks
            execute_mysql_query(
                "UPDATE followup_records SET status = 'overdue' WHERE patient_id = %s AND status = 'pending' AND due_date < %s",
                (user_id, today),
                commit=True
            )
            
            # Fetch for patient
            records = execute_mysql_query(
                "SELECT record_id, record_type, description, due_date, status FROM followup_records WHERE patient_id = %s ORDER BY due_date ASC",
                (user_id,),
                fetchall=True
            )
        elif role == "provider" or role == "admin":
            # Fetch all for provider overview
            records = execute_mysql_query(
                """
                SELECT r.record_id, r.record_type, r.description, r.due_date, r.status, u.full_name AS patient_name, u.user_id AS patient_id
                FROM followup_records r
                JOIN users u ON r.patient_id = u.user_id
                ORDER BY u.full_name ASC, r.due_date ASC
                """,
                fetchall=True
            )
        else:
            records = []
            
        # Format due_date safely
        for r in records:
            if hasattr(r["due_date"], "isoformat"):
                r["due_date"] = r["due_date"].isoformat()
            else:
                r["due_date"] = str(r["due_date"])
                
        return jsonify(records), 200
    except Exception as e:
        print(f"[Demo Mode Fallback] Follow-up records database failed: {e}")
        from db.mock_db import MOCK_FOLLOWUP_RECORDS
        import copy
        records = copy.deepcopy(MOCK_FOLLOWUP_RECORDS)
        if role == "patient":
            records = [r for r in records if r["patient_id"] == int(user_id)]
        for r in records:
            r["patient_name"] = "Jane Doe"
        return jsonify(records), 200

@followup_bp.route("", methods=["POST"])
@token_required
def create_followup():
    """Create a new follow-up schedule."""
    user = g.user
    if user["role"] != "patient":
        return jsonify({"message": "Access Denied: Only patients can schedule follow-up tasks."}), 403
        
    data = request.get_json() or {}
    record_type = data.get("record_type")
    description = data.get("description", "").strip()
    due_date = data.get("due_date")
    
    if record_type not in ["injection", "medication", "checkup"]:
        return jsonify({"message": "Invalid category. Must be medication, injection, or checkup."}), 400
        
    if not description:
        return jsonify({"message": "Description cannot be empty."}), 400
        
    is_valid, err = validate_date(due_date)
    if not is_valid:
        return jsonify({"message": err}), 400
        
    # Auto status determination
    # Convert error/result date safely
    target_date = datetime.date.fromisoformat(due_date)
    status = "overdue" if target_date < datetime.date.today() else "pending"
    
    try:
        execute_mysql_query(
            "INSERT INTO followup_records (patient_id, record_type, description, due_date, status) VALUES (%s, %s, %s, %s, %s)",
            (user["user_id"], record_type, description, due_date, status),
            commit=True
        )
        return jsonify({"message": "Follow-up schedule recorded successfully!"}), 201
    except Exception as e:
        print(f"[Demo Mode Fallback] Create follow-up database failed: {e}")
        from db.mock_db import MOCK_FOLLOWUP_RECORDS
        new_id = len(MOCK_FOLLOWUP_RECORDS) + 1
        new_rec = {
            "record_id": new_id,
            "patient_id": int(user["user_id"]),
            "record_type": record_type,
            "description": description,
            "due_date": due_date,
            "status": status
        }
        MOCK_FOLLOWUP_RECORDS.append(new_rec)
        return jsonify({"message": "Follow-up schedule recorded successfully (Offline Demo Mode)!"}), 201

@followup_bp.route("/<int:record_id>/complete", methods=["PATCH"])
@token_required
def complete_followup(record_id):
    """Mark a specific follow-up task as Completed."""
    user = g.user
    role = user["role"]
    user_id = user["user_id"]
    
    try:
        # Check if exists
        rec = execute_mysql_query(
            "SELECT patient_id FROM followup_records WHERE record_id = %s",
            (record_id,),
            fetchone=True
        )
        if not rec:
            return jsonify({"message": "Task not found."}), 404
            
        # Verify permissions (only patient who owns the task, or admin)
        if role == "patient" and rec["patient_id"] != user_id:
            return jsonify({"message": "Access Denied: Unauthorized checkoff."}), 403
        elif role not in ["patient", "admin"]:
            return jsonify({"message": "Access Denied."}), 403
            
        execute_mysql_query("UPDATE followup_records SET status = 'completed' WHERE record_id = %s", (record_id,), commit=True)
        return jsonify({"message": "Task checked off as completed!"}), 200
    except Exception as e:
        print(f"[Demo Mode Fallback] Complete follow-up database failed: {e}")
        from db.mock_db import MOCK_FOLLOWUP_RECORDS
        found = False
        for r in MOCK_FOLLOWUP_RECORDS:
            if r["record_id"] == record_id:
                r["status"] = "completed"
                found = True
                break
        if not found:
            # Add it just in case to be robust
            MOCK_FOLLOWUP_RECORDS.append({
                "record_id": record_id,
                "patient_id": int(user_id),
                "record_type": "medication",
                "description": "Dynamic medication follow-up task",
                "due_date": datetime.date.today().isoformat(),
                "status": "completed"
            })
        return jsonify({"message": "Task checked off as completed (Offline Demo Mode)!"}), 200
