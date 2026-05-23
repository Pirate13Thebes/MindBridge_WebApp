import datetime
from flask import Blueprint, request, jsonify, g, Response
from db.mysql_db import execute_mysql_query
from db.mongo_db import get_mongo_db
from api.middleware import token_required, admin_required, patient_required
from utils.exporter import generate_patient_csv

admin_bp = Blueprint("admin_bp", __name__)

@admin_bp.route("/admin/stats", methods=["GET"])
@token_required
@admin_required
def get_stats():
    """Retrieve global system performance statistics and counts (Admin only)."""
    try:
        users_count = execute_mysql_query("SELECT COUNT(*) AS c FROM users", fetchone=True)["c"]
        sessions_count = execute_mysql_query("SELECT COUNT(*) AS c FROM therapy_sessions", fetchone=True)["c"]
        followups_count = execute_mysql_query("SELECT COUNT(*) AS c FROM followup_records", fetchone=True)["c"]
        articles_count = execute_mysql_query("SELECT COUNT(*) AS c FROM articles", fetchone=True)["c"]
        
        db = get_mongo_db()
        journals_count = db.journal_entries.count_documents({})
        exercises_count = db.exercises.count_documents({})
        support_count = db.support_resources.count_documents({})
        
        return jsonify({
            "users": users_count,
            "therapy_sessions": sessions_count,
            "followup_records": followups_count,
            "articles": articles_count,
            "journals": journals_count,
            "exercises": exercises_count,
            "support_resources": support_count
        }), 200
    except Exception as e:
        print(f"[Demo Mode Fallback] Admin stats database failed: {e}")
        from db.mock_db import get_mock_stats
        return jsonify(get_mock_stats()), 200

@admin_bp.route("/admin/users", methods=["GET"])
@token_required
@admin_required
def get_users():
    """Retrieve lists of all registered users (Admin only)."""
    try:
        users = execute_mysql_query(
            "SELECT user_id, username, role, full_name, created_at FROM users ORDER BY user_id ASC",
            fetchall=True
        )
        for u in users:
            if hasattr(u["created_at"], "isoformat"):
                u["created_at"] = u["created_at"].isoformat()
            else:
                u["created_at"] = str(u["created_at"])
                
        return jsonify(users), 200
    except Exception as e:
        print(f"[Demo Mode Fallback] Admin users directory database failed: {e}")
        from db.mock_db import get_mock_users
        import copy
        users = copy.deepcopy(get_mock_users())
        for u in users:
            u.pop("password_hash", None)
            if hasattr(u.get("created_at"), "isoformat"):
                u["created_at"] = u["created_at"].isoformat()
            else:
                u["created_at"] = str(u.get("created_at", ""))
        return jsonify(users), 200

@admin_bp.route("/admin/export/<int:patient_id>", methods=["GET"])
@token_required
@admin_required
def export_patient_profile(patient_id):
    """Compile and stream the Patient's profile history as a CSV attachment (Admin only)."""
    try:
        csv_content = generate_patient_csv(patient_id)
        if csv_content.startswith("Error"):
            return jsonify({"message": csv_content}), 404
            
        return Response(
            csv_content,
            mimetype="text/csv",
            headers={"Content-disposition": f"attachment; filename=patient_{patient_id}_history.csv"}
        )
    except Exception as e:
        return jsonify({"message": f"Server error generating export: {e}"}), 500

@admin_bp.route("/dashboard/reminders", methods=["GET"])
@token_required
@patient_required
def get_dashboard_reminders():
    """Retrieve personalized notification alerts for the logged-in patient."""
    user = g.user
    patient_id = user["user_id"]
    today = datetime.date.today()
    
    try:
        # Auto-flag overdue tasks in background
        execute_mysql_query(
            "UPDATE followup_records SET status = 'overdue' WHERE patient_id = %s AND status = 'pending' AND due_date < %s",
            (patient_id, today),
            commit=True
        )
        
        # 1. Check for overdue tasks
        overdue = execute_mysql_query(
            "SELECT record_type, description, due_date FROM followup_records WHERE patient_id = %s AND status = 'overdue' ORDER BY due_date ASC",
            (patient_id,),
            fetchall=True
        ) or []
        
        # 2. Check for upcoming therapy sessions
        sessions = execute_mysql_query(
            """
            SELECT s.session_date, u.full_name AS therapist_name 
            FROM therapy_sessions s
            JOIN users u ON s.therapist_id = u.user_id
            WHERE s.patient_id = %s AND s.status = 'scheduled' AND s.session_date >= %s
            ORDER BY s.session_date ASC
            """,
            (patient_id, today),
            fetchall=True
        ) or []
        
        reminders_list = []
        for o in overdue:
            due_str = o["due_date"].strftime("%Y-%m-%d") if hasattr(o["due_date"], "strftime") else str(o["due_date"])
            reminders_list.append({
                "type": "overdue",
                "message": f"Overdue task: Take your [{o['record_type'].upper()}] - '{o['description']}' (Was due: {due_str})"
            })
            
        for s in sessions:
            sess_str = s["session_date"].strftime("%Y-%m-%d") if hasattr(s["session_date"], "strftime") else str(s["session_date"])
            reminders_list.append({
                "type": "therapy",
                "message": f"Upcoming scheduled therapy session with {s['therapist_name']} on {sess_str}"
            })
            
        return jsonify(reminders_list), 200
    except Exception as e:
        return jsonify({"message": f"Server error generating reminders: {e}"}), 500
