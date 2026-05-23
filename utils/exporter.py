import csv
import io
from db.mysql_db import execute_mysql_query
from db.mongo_db import get_mongo_db

def generate_patient_csv(patient_id):
    """
    Generate a merged, flat CSV of all data for a specific patient.
    Merges:
      - MySQL users (profile details)
      - MySQL therapy_sessions (clinical schedules)
      - MySQL followup_records (medications & checkups)
      - MongoDB journal_entries (unstructured logs & mood)
    
    Returns a string containing the CSV content.
    """
    try:
        # 1. Fetch Patient profile
        patient = execute_mysql_query(
            "SELECT user_id, username, full_name, role FROM users WHERE user_id = %s",
            (patient_id,),
            fetchone=True
        )
        if not patient:
            return "Error: Patient not found."
        
        # 2. Fetch MySQL therapy sessions for the patient
        sessions = execute_mysql_query(
            """
            SELECT 
                s.session_id, 
                s.session_date, 
                s.notes, 
                s.status,
                t.full_name AS therapist_name
            FROM therapy_sessions s
            JOIN users t ON s.therapist_id = t.user_id
            WHERE s.patient_id = %s
            ORDER BY s.session_date DESC
            """,
            (patient_id,),
            fetchall=True
        ) or []
        
        # 3. Fetch MySQL followups for the patient
        followups = execute_mysql_query(
            """
            SELECT record_id, record_type, description, due_date, status
            FROM followup_records
            WHERE patient_id = %s
            ORDER BY due_date DESC
            """,
            (patient_id,),
            fetchall=True
        ) or []
        
        # 4. Fetch MongoDB journals for the patient
        db = get_mongo_db()
        journals = list(db.journal_entries.find({"patient_id": int(patient_id)}).sort("created_at", -1))
        
        output = io.StringIO()
        writer = csv.writer(output)
        
        # Header
        writer.writerow([
            "Patient ID", "Username", "Full Name", 
            "Data Type", "Record ID", "Date", 
            "Label/Category", "Status/Mood", "Description/Notes"
        ])
        
        # Row merger & streamer
        # Relational: Therapy Sessions
        for s in sessions:
            writer.writerow([
                patient["user_id"],
                patient["username"],
                patient["full_name"],
                "Therapy Session",
                s["session_id"],
                str(s["session_date"]),
                f"Therapist: {s['therapist_name']}",
                s["status"],
                s["notes"] or ""
            ])
            
        # Relational: Followups
        for f in followups:
            writer.writerow([
                patient["user_id"],
                patient["username"],
                patient["full_name"],
                "Follow-up Task",
                f["record_id"],
                str(f["due_date"]),
                f["record_type"],
                f["status"],
                f["description"]
            ])
            
        # Unstructured: Journal Entries
        for j in journals:
            writer.writerow([
                patient["user_id"],
                patient["username"],
                patient["full_name"],
                "Mood Journal Entry",
                str(j["_id"]),
                j["created_at"].strftime("%Y-%m-%d %H:%M:%S") if hasattr(j["created_at"], "strftime") else str(j["created_at"]),
                "Patient Journal",
                j["mood"],
                j["content"]
            ])
            
        csv_string = output.getvalue()
        output.close()
        return csv_string
    except Exception as e:
        print(f"[Demo Mode Fallback] CSV export database query failed: {e}")
        from db.mock_db import get_mock_user_by_id, MOCK_THERAPY_SESSIONS, MOCK_FOLLOWUP_RECORDS, MOCK_JOURNALS
        
        patient = get_mock_user_by_id(patient_id)
        if not patient:
            # Fallback to the first mock user (Patient ID 1) if requesting an unknown ID
            patient = get_mock_user_by_id(1)
            
        if not patient:
            return "Error: Patient not found."
            
        # Filter mock records
        sessions = [s for s in MOCK_THERAPY_SESSIONS if s["patient_id"] == patient["user_id"]]
        followups = [f for f in MOCK_FOLLOWUP_RECORDS if f["patient_id"] == patient["user_id"]]
        journals = [j for j in MOCK_JOURNALS if j["patient_id"] == patient["user_id"]]
        
        output = io.StringIO()
        writer = csv.writer(output)
        
        # Header
        writer.writerow([
            "Patient ID", "Username", "Full Name", 
            "Data Type", "Record ID", "Date", 
            "Label/Category", "Status/Mood", "Description/Notes"
        ])
        
        # Row merger & streamer for mock data
        for idx, s in enumerate(sessions):
            writer.writerow([
                patient["user_id"],
                patient["username"],
                patient["full_name"],
                "Therapy Session",
                f"SESS-MOCK-{idx+100}",
                str(s["session_date"]),
                "Therapist: Dr. Sarah Jenkins",
                s["status"],
                s["notes"]
            ])
            
        for idx, f in enumerate(followups):
            writer.writerow([
                patient["user_id"],
                patient["username"],
                patient["full_name"],
                "Follow-up Task",
                f"TASK-MOCK-{idx+100}",
                str(f["due_date"]),
                f["record_type"],
                f["status"],
                f["description"]
            ])
            
        for idx, j in enumerate(journals):
            writer.writerow([
                patient["user_id"],
                patient["username"],
                patient["full_name"],
                "Mood Journal Entry",
                f"MONGO-MOCK-{idx+100}",
                str(j["created_at"]),
                "Patient Journal",
                j["mood"],
                j["content"]
            ])
            
        csv_string = output.getvalue()
        output.close()
        return csv_string
