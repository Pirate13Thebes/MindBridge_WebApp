from flask import Blueprint, request, jsonify, g
from db.mysql_db import execute_mysql_query
from api.middleware import token_required
from utils.validators import validate_date

therapy_bp = Blueprint("therapy_bp", __name__)

@therapy_bp.route("", methods=["GET"])
@token_required
def get_sessions():
    """Retrieve therapy sessions filtered by role access."""
    user = g.user
    role = user["role"]
    user_id = user["user_id"]
    
    try:
        if role == "patient":
            sessions = execute_mysql_query(
                """
                SELECT s.session_id, s.session_date, s.notes, s.status, 
                       p.full_name AS patient_name, t.full_name AS therapist_name
                FROM therapy_sessions s
                JOIN users p ON s.patient_id = p.user_id
                JOIN users t ON s.therapist_id = t.user_id
                WHERE s.patient_id = %s
                ORDER BY s.session_date ASC
                """,
                (user_id,),
                fetchall=True
            )
        elif role == "provider":
            sessions = execute_mysql_query(
                """
                SELECT s.session_id, s.session_date, s.notes, s.status, 
                       p.full_name AS patient_name, t.full_name AS therapist_name
                FROM therapy_sessions s
                JOIN users p ON s.patient_id = p.user_id
                JOIN users t ON s.therapist_id = t.user_id
                WHERE s.therapist_id = %s
                ORDER BY s.session_date ASC
                """,
                (user_id,),
                fetchall=True
            )
        elif role == "admin":
            sessions = execute_mysql_query(
                """
                SELECT s.session_id, s.session_date, s.notes, s.status, 
                       p.full_name AS patient_name, t.full_name AS therapist_name
                FROM therapy_sessions s
                JOIN users p ON s.patient_id = p.user_id
                JOIN users t ON s.therapist_id = t.user_id
                ORDER BY s.session_date DESC
                """,
                fetchall=True
            )
        else:
            sessions = []
            
        # Format dates in output safely
        for s in sessions:
            if hasattr(s["session_date"], "isoformat"):
                s["session_date"] = s["session_date"].isoformat()
            else:
                s["session_date"] = str(s["session_date"])
                
        return jsonify(sessions), 200
    except Exception as e:
        print(f"[Demo Mode Fallback] Therapy sessions database failed: {e}")
        from db.mock_db import MOCK_THERAPY_SESSIONS
        import copy
        sessions = copy.deepcopy(MOCK_THERAPY_SESSIONS)
        for s in sessions:
            s["patient_name"] = "Jane Doe"
            s["therapist_name"] = "Dr. Sarah Jenkins"
        return jsonify(sessions), 200

@therapy_bp.route("", methods=["POST"])
@token_required
def book_session():
    """Patient schedules a new session."""
    user = g.user
    if user["role"] != "patient":
        return jsonify({"message": "Access Denied: Only patients can book clinical sessions."}), 403
        
    data = request.get_json() or {}
    therapist_id = data.get("therapist_id")
    session_date = data.get("session_date")
    notes = data.get("notes", "").strip()
    
    if not therapist_id or not session_date:
        return jsonify({"message": "Therapist ID and session date are required."}), 400
        
    is_valid, err = validate_date(session_date)
    if not is_valid:
        return jsonify({"message": err}), 400
        
    try:
        # Check if therapist exists and is provider
        therapist = execute_mysql_query(
            "SELECT full_name FROM users WHERE user_id = %s AND role = 'provider'",
            (therapist_id,),
            fetchone=True
        )
        if not therapist:
            return jsonify({"message": "Selected specialist is not registered or not active."}), 400
            
        execute_mysql_query(
            "INSERT INTO therapy_sessions (patient_id, therapist_id, session_date, notes, status) VALUES (%s, %s, %s, %s, 'scheduled')",
            (user["user_id"], therapist_id, session_date, notes or None),
            commit=True
        )
        return jsonify({"message": "Therapy session booked successfully!"}), 201
    except Exception as e:
        print(f"[Demo Mode Fallback] Book session database failed: {e}")
        from db.mock_db import MOCK_THERAPY_SESSIONS
        new_id = len(MOCK_THERAPY_SESSIONS) + 1
        MOCK_THERAPY_SESSIONS.append({
            "session_id": new_id,
            "patient_id": int(user["user_id"]),
            "therapist_id": int(therapist_id),
            "session_date": session_date,
            "notes": notes,
            "status": "scheduled"
        })
        return jsonify({"message": "Therapy session booked successfully (Offline Demo Mode)!"}), 201

@therapy_bp.route("/<int:session_id>", methods=["PATCH"])
@token_required
def update_session(session_id):
    """Update therapy session details or status (e.g., complete or cancel)."""
    user = g.user
    role = user["role"]
    user_id = user["user_id"]
    
    data = request.get_json() or {}
    new_status = data.get("status")
    notes = data.get("notes")
    
    if new_status not in ["scheduled", "completed", "cancelled"]:
        return jsonify({"message": "Invalid status value."}), 400
        
    try:
        # Check if session exists
        sess = execute_mysql_query(
            "SELECT patient_id, therapist_id, status FROM therapy_sessions WHERE session_id = %s",
            (session_id,),
            fetchone=True
        )
        if not sess:
            return jsonify({"message": "Appointment not found."}), 404
            
        # Role authorizations
        if role == "patient":
            # Patient can only cancel their own scheduled sessions
            if sess["patient_id"] != user_id:
                return jsonify({"message": "Access Denied."}), 403
            if new_status != "cancelled":
                return jsonify({"message": "Patients are only authorized to cancel scheduled sessions."}), 403
        elif role == "provider":
            # Provider can mark completed/cancelled on their own roster
            if sess["therapist_id"] != user_id:
                return jsonify({"message": "Access Denied."}), 403
        elif role != "admin":
            return jsonify({"message": "Access Denied."}), 403
            
        # Compile updates
        update_fields = []
        params = []
        if new_status:
            update_fields.append("status = %s")
            params.append(new_status)
        if notes is not None:
            update_fields.append("notes = %s")
            params.append(notes)
            
        params.append(session_id)
        
        execute_mysql_query(
            f"UPDATE therapy_sessions SET {', '.join(update_fields)} WHERE session_id = %s",
            tuple(params),
            commit=True
        )
        return jsonify({"message": "Session details successfully updated."}), 200
    except Exception as e:
        return jsonify({"message": f"Server error during update: {e}"}), 500

@therapy_bp.route("/<int:session_id>", methods=["DELETE"])
@token_required
def delete_session(session_id):
    """Admin or Patient cancels/removes session."""
    user = g.user
    role = user["role"]
    user_id = user["user_id"]
    
    try:
        sess = execute_mysql_query(
            "SELECT patient_id FROM therapy_sessions WHERE session_id = %s",
            (session_id,),
            fetchone=True
        )
        if not sess:
            return jsonify({"message": "Session not found."}), 404
            
        if role == "patient" and sess["patient_id"] != user_id:
            return jsonify({"message": "Access Denied: Unauthorized cancellation."}), 403
        elif role not in ["patient", "admin"]:
            return jsonify({"message": "Access Denied."}), 403
            
        execute_mysql_query("DELETE FROM therapy_sessions WHERE session_id = %s", (session_id,), commit=True)
        return jsonify({"message": "Appointment cancelled and removed from database."}), 200
    except Exception as e:
        return jsonify({"message": f"Server error: {e}"}), 500
