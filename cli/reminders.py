import datetime
from db.mysql_db import execute_mysql_query

def show_reminders(session):
    """
    On login reminder engine.
    Scans for overdue follow-up records and upcoming therapy sessions for the logged-in patient.
    """
    if session["role"] != "patient":
        return
        
    print("\n" + "="*50)
    print("           MINDBRIDGE HEALTH REMINDERS")
    print("="*50)
    
    patient_id = session["user_id"]
    today = datetime.date.today()
    
    overdue_tasks = []
    upcoming_sessions = []
    
    try:
        # 1. Update status to 'overdue' for pending tasks whose due_date < today
        execute_mysql_query(
            "UPDATE followup_records SET status = 'overdue' WHERE patient_id = %s AND status = 'pending' AND due_date < %s",
            (patient_id, today),
            commit=True
        )
        
        # 2. Fetch overdue follow-up tasks
        overdue_tasks = execute_mysql_query(
            "SELECT record_id, record_type, description, due_date FROM followup_records WHERE patient_id = %s AND status = 'overdue' ORDER BY due_date ASC",
            (patient_id,),
            fetchall=True
        ) or []
        
        # 3. Fetch upcoming scheduled therapy sessions
        upcoming_sessions = execute_mysql_query(
            """
            SELECT s.session_id, s.session_date, u.full_name AS therapist_name 
            FROM therapy_sessions s
            JOIN users u ON s.therapist_id = u.user_id
            WHERE s.patient_id = %s AND s.status = 'scheduled' AND s.session_date >= %s
            ORDER BY s.session_date ASC
            """,
            (patient_id, today),
            fetchall=True
        ) or []
        
    except Exception:
        # Mock mode fallback if DB not running/configured yet in this environment
        print("[Demo Notification] Database is offline. Displaying simulated patient reminders:")
        overdue_tasks = [{
            "record_type": "medication",
            "description": "Daily post-natal vitamins and iron supplements",
            "due_date": today - datetime.timedelta(days=2)
        }]
        upcoming_sessions = [{
            "therapist_name": "Dr. Sarah Jenkins (PPD Specialist)",
            "session_date": today + datetime.timedelta(days=1)
        }]
        
    # Print Reminders Banners
    alerts_triggered = False
    
    if overdue_tasks:
        alerts_triggered = True
        print("\n\033[91m⚠️  WARNING: YOU HAVE OVERDUE FOLLOW-UP TASKS:\033[0m")
        for task in overdue_tasks:
            due_str = task["due_date"].strftime("%Y-%m-%d") if hasattr(task["due_date"], "strftime") else str(task["due_date"])
            print(f"  • [{task['record_type'].upper()}] - {task['description']} (Was due: {due_str})")
            
    if upcoming_sessions:
        alerts_triggered = True
        print("\n\033[92m📅 UPCOMING THERAPY SESSIONS:\033[0m")
        for sess in upcoming_sessions:
            sess_str = sess["session_date"].strftime("%Y-%m-%d") if hasattr(sess["session_date"], "strftime") else str(sess["session_date"])
            print(f"  • Session with {sess['therapist_name']} on {sess_str}")
            
    if not alerts_triggered:
        print("\n✨ You are all caught up! No overdue tasks or upcoming therapy sessions today.")
        
    print("\n" + "="*50)
