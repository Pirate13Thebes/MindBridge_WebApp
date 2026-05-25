import datetime
from db.mysql_db import execute_mysql_query
from utils.validators import validate_date

def run(session):
    """Entry point for Therapy module."""
    role = session["role"]
    
    while True:
        print("\n=== Therapy Sessions Management ===")
        if role == "patient":
            print("[1] Book a Therapy Session")
            print("[2] View My Scheduled Sessions")
            print("[3] Cancel a Therapy Session")
            print("[0] Return to Main Menu")
        elif role == "provider":
            print("[1] View My Session Roster")
            print("[2] Complete a Therapy Session")
            print("[3] Cancel a Therapy Session")
            print("[0] Return to Main Menu")
        elif role == "admin":
            print("[1] View All Sessions in System")
            print("[0] Return to Main Menu")
        else:
            print("Access Denied: Only patients, providers, and admins can manage therapy sessions.")
            return

        choice = input("Enter choice: ").strip()
        if choice == "0":
            break
            
        if role == "patient":
            if choice == "1":
                book_session_patient(session)
            elif choice == "2":
                view_sessions_patient(session)
            elif choice == "3":
                cancel_session_patient(session)
        elif role == "provider":
            if choice == "1":
                view_sessions_provider(session)
            elif choice == "2":
                complete_session_provider(session)
            elif choice == "3":
                cancel_session_provider(session)
        elif role == "admin":
            if choice == "1":
                view_all_sessions_admin()

def book_session_patient(session):
    """Patient books a new therapy session with a provider."""
    print("\n--- Book Therapy Session ---")
    try:
        # Fetch available therapists
        therapists = execute_mysql_query(
            "SELECT user_id, full_name FROM users WHERE role = 'provider'",
            fetchall=True
        )
        if not therapists:
            print("No professional therapists are currently registered on the system.")
            return
            
        print("Available Mental Health Specialists:")
        for t in therapists:
            print(f"  [{t['user_id']}] - {t['full_name']}")
            
        t_id_str = input("\nEnter Therapist ID: ").strip()
        try:
            t_id = int(t_id_str)
        except ValueError:
            print("Error: Invalid Therapist ID.")
            return
            
        if t_id not in [t["user_id"] for t in therapists]:
            print("Error: Specialist not found.")
            return
            
        while True:
            date_str = input("Enter appointment date (YYYY-MM-DD): ").strip()
            is_valid, parsed_date = validate_date(date_str)
            if not is_valid:
                print(f"Error: {parsed_date}")
                continue
            if parsed_date < datetime.date.today():
                print("Error: Cannot book appointments in the past.")
                continue
            break
            
        notes = input("Enter reason/notes for session (optional): ").strip()
        
        execute_mysql_query(
            "INSERT INTO therapy_sessions (patient_id, therapist_id, session_date, notes, status) VALUES (%s, %s, %s, %s, 'scheduled')",
            (session["user_id"], t_id, date_str, notes or None),
            commit=True
        )
        print("\nSuccess: Therapy session booked successfully!")
    except Exception as e:
        print(f"Error: Could not schedule session ({e}). Database might be in offline demo mode.")

def view_sessions_patient(session):
    """View patient's scheduled clinical sessions."""
    print("\n--- My Scheduled Sessions ---")
    try:
        sessions = execute_mysql_query(
            """
            SELECT s.session_id, s.session_date, s.notes, s.status, u.full_name AS therapist_name
            FROM therapy_sessions s
            JOIN users u ON s.therapist_id = u.user_id
            WHERE s.patient_id = %s
            ORDER BY s.session_date ASC
            """,
            (session["user_id"],),
            fetchall=True
        )
        
        if not sessions:
            print("You have no scheduled clinical sessions.")
            return
            
        for s in sessions:
            date_str = s["session_date"].strftime("%Y-%m-%d") if hasattr(s["session_date"], "strftime") else str(s["session_date"])
            print(f"ID: {s['session_id']} | Date: {date_str} | Therapist: {s['therapist_name']} | Status: {s['status'].upper()}")
            print(f"  Notes: {s['notes'] or 'None'}")
            print("-" * 50)
    except Exception as e:
        print(f"Offline Mode: Simulating mock therapy details: {e}")

def cancel_session_patient(session):
    """Patient cancels their scheduled session."""
    view_sessions_patient(session)
    sess_id_str = input("\nEnter Session ID to cancel: ").strip()
    try:
        sess_id = int(sess_id_str)
    except ValueError:
        print("Error: Invalid ID.")
        return
        
    try:
        # Verify ownership
        sess = execute_mysql_query(
            "SELECT session_id FROM therapy_sessions WHERE session_id = %s AND patient_id = %s AND status = 'scheduled'",
            (sess_id, session["user_id"]),
            fetchone=True
        )
        if not sess:
            print("Error: Active session not found or already completed/cancelled.")
            return
            
        execute_mysql_query(
            "UPDATE therapy_sessions SET status = 'cancelled' WHERE session_id = %s",
            (sess_id,),
            commit=True
        )
        print("Success: Therapy session was successfully cancelled.")
    except Exception as e:
        print(f"Error executing cancel command: {e}")

def view_sessions_provider(session):
    """Provider views their rosters."""
    print("\n--- My Session Roster ---")
    try:
        sessions = execute_mysql_query(
            """
            SELECT s.session_id, s.session_date, s.notes, s.status, u.full_name AS patient_name
            FROM therapy_sessions s
            JOIN users u ON s.patient_id = u.user_id
            WHERE s.therapist_id = %s
            ORDER BY s.session_date ASC
            """,
            (session["user_id"],),
            fetchall=True
        )
        
        if not sessions:
            print("No clients have booked sessions in your roster.")
            return
            
        for s in sessions:
            date_str = s["session_date"].strftime("%Y-%m-%d") if hasattr(s["session_date"], "strftime") else str(s["session_date"])
            print(f"ID: {s['session_id']} | Date: {date_str} | Client: {s['patient_name']} | Status: {s['status'].upper()}")
            print(f"  Notes: {s['notes'] or 'None'}")
            print("-" * 50)
    except Exception as e:
        print(f"Error querying roster: {e}")

def complete_session_provider(session):
    """Mark session as completed."""
    view_sessions_provider(session)
    sess_id_str = input("\nEnter Session ID to mark as Completed: ").strip()
    try:
        sess_id = int(sess_id_str)
    except ValueError:
        print("Error: Invalid ID.")
        return
        
    try:
        sess = execute_mysql_query(
            "SELECT session_id FROM therapy_sessions WHERE session_id = %s AND therapist_id = %s AND status = 'scheduled'",
            (sess_id, session["user_id"]),
            fetchone=True
        )
        if not sess:
            print("Error: Active scheduled session not found.")
            return
            
        execute_mysql_query(
            "UPDATE therapy_sessions SET status = 'completed' WHERE session_id = %s",
            (sess_id,),
            commit=True
        )
        print("Success: Session successfully marked as COMPLETED.")
    except Exception as e:
        print(f"Error updating session status: {e}")

def cancel_session_provider(session):
    """Mark session as cancelled by provider."""
    view_sessions_provider(session)
    sess_id_str = input("\nEnter Session ID to cancel: ").strip()
    try:
        sess_id = int(sess_id_str)
    except ValueError:
        print("Error: Invalid ID.")
        return
        
    try:
        sess = execute_mysql_query(
            "SELECT session_id FROM therapy_sessions WHERE session_id = %s AND therapist_id = %s AND status = 'scheduled'",
            (sess_id, session["user_id"]),
            fetchone=True
        )
        if not sess:
            print("Error: Active scheduled session not found.")
            return
            
        execute_mysql_query(
            "UPDATE therapy_sessions SET status = 'cancelled' WHERE session_id = %s",
            (sess_id,),
            commit=True
        )
        print("Success: Session successfully cancelled.")
    except Exception as e:
        print(f"Error cancelling session: {e}")

def view_all_sessions_admin():
    """Admin reads all sessions in database."""
    print("\n--- All Therapy Sessions in System ---")
    try:
        sessions = execute_mysql_query(
            """
            SELECT s.session_id, s.session_date, s.status, 
                   p.full_name AS patient_name, t.full_name AS therapist_name
            FROM therapy_sessions s
            JOIN users p ON s.patient_id = p.user_id
            JOIN users t ON s.therapist_id = t.user_id
            ORDER BY s.session_date DESC
            """,
            fetchall=True
        )
        if not sessions:
            print("No therapy sessions recorded in the database.")
            return
            
        for s in sessions:
            date_str = s["session_date"].strftime("%Y-%m-%d") if hasattr(s["session_date"], "strftime") else str(s["session_date"])
            print(f"ID: {s['session_id']} | Date: {date_str} | Client: {s['patient_name']} | Therapist: {s['therapist_name']} | Status: {s['status'].upper()}")
    except Exception as e:
        print(f"Error retrieving sessions: {e}")

# Updated by fkangira
