import datetime
from db.mysql_db import execute_mysql_query
from utils.validators import validate_date

def run(session):
    """Entry point for Followup module."""
    role = session["role"]
    
    while True:
        print("\n=== Postpartum Follow-up Tracker ===")
        if role == "patient":
            print("[1] Log a New Follow-up Schedule")
            print("[2] List My Follow-up Schedule")
            print("[3] Complete a Follow-up Task")
            print("[0] Return to Main Menu")
        elif role == "provider":
            print("[1] View Patients' Compliance Overview")
            print("[0] Return to Main Menu")
        else:
            print("Access Denied: Only patients and providers can interact with follow-up trackers.")
            return

        choice = input("Enter choice: ").strip()
        if choice == "0":
            break
            
        if role == "patient":
            if choice == "1":
                add_followup_patient(session)
            elif choice == choice == "2":
                list_followup_patient(session)
            elif choice == "3":
                complete_followup_patient(session)
        elif role == "provider":
            if choice == "1":
                view_compliance_provider()

def add_followup_patient(session):
    """Patient logs a new follow-up medication or checkup task."""
    print("\n--- Add Follow-up Task ---")
    print("Select Schedule Category:")
    print("[1] Medication (pills, iron supplements, etc.)")
    print("[2] Injection (clinical shots, hormones, etc.)")
    print("[3] Checkup (pediatrician, postpartum recovery, etc.)")
    
    type_map = {"1": "medication", "2": "injection", "3": "checkup"}
    while True:
        choice = input("Enter option (1-3): ").strip()
        if choice in type_map:
            rec_type = type_map[choice]
            break
        print("Invalid option. Enter 1, 2, or 3.")
        
    description = input("Task Description (e.g., Take Prenatal Iron Complex 50mg): ").strip()
    if not description:
        print("Error: Description cannot be empty.")
        return
        
    while True:
        date_str = input("Due Date (YYYY-MM-DD): ").strip()
        is_valid, parsed_date = validate_date(date_str)
        if not is_valid:
            print(f"Error: {parsed_date}")
            continue
        break
        
    # Auto-flag status as overdue if due in the past
    status = "overdue" if parsed_date < datetime.date.today() else "pending"
    
    try:
        execute_mysql_query(
            "INSERT INTO followup_records (patient_id, record_type, description, due_date, status) VALUES (%s, %s, %s, %s, %s)",
            (session["user_id"], rec_type, description, date_str, status),
            commit=True
        )
        print("\nSuccess: Follow-up schedule saved!")
    except Exception as e:
        print(f"Error: Could not save schedule ({e}).")

def list_followup_patient(session):
    """List a patient's individual schedule."""
    print("\n--- My Follow-up Schedule ---")
    patient_id = session["user_id"]
    today = datetime.date.today()
    
    try:
        # First, auto-flag past due tasks as overdue in database
        execute_mysql_query(
            "UPDATE followup_records SET status = 'overdue' WHERE patient_id = %s AND status = 'pending' AND due_date < %s",
            (patient_id, today),
            commit=True
        )
        
        # Now fetch all
        records = execute_mysql_query(
            "SELECT record_id, record_type, description, due_date, status FROM followup_records WHERE patient_id = %s ORDER BY due_date ASC",
            (patient_id,),
            fetchall=True
        )
        
        if not records:
            print("Your follow-up tracker is currently empty.")
            return
            
        for r in records:
            due_str = r["due_date"].strftime("%Y-%m-%d") if hasattr(r["due_date"], "strftime") else str(r["due_date"])
            
            # Stylize status text
            status_text = r["status"].upper()
            if r["status"] == "overdue":
                status_text = f"\033[91m{status_text} ⚠️\033[0m"
            elif r["status"] == "completed":
                status_text = f"\033[92m{status_text} ✓\033[0m"
            else:
                status_text = f"\033[94m{status_text}\033[0m"
                
            print(f"ID: {r['record_id']} | Type: {r['record_type'].capitalize()} | Due: {due_str} | Status: {status_text}")
            print(f"  Description: {r['description']}")
            print("-" * 50)
            
    except Exception as e:
        print(f"Error loading follow-ups: {e}")

def complete_followup_patient(session):
    """Mark a pending/overdue task as Completed."""
    list_followup_patient(session)
    rec_id_str = input("\nEnter Task ID to mark as Completed: ").strip()
    try:
        rec_id = int(rec_id_str)
    except ValueError:
        print("Error: Invalid ID.")
        return
        
    try:
        # Verify ownership
        rec = execute_mysql_query(
            "SELECT record_id FROM followup_records WHERE record_id = %s AND patient_id = %s",
            (rec_id, session["user_id"]),
            fetchone=True
        )
        if not rec:
            print("Error: Task not found.")
            return
            
        execute_mysql_query(
            "UPDATE followup_records SET status = 'completed' WHERE record_id = %s",
            (rec_id,),
            commit=True
        )
        print("Success: Task checked off! Well done on staying compliant.")
    except Exception as e:
        print(f"Error completing task: {e}")

def view_compliance_provider():
    """Provider lists compliance of all patients in system."""
    print("\n--- Patients' Care Compliance Overview ---")
    try:
        records = execute_mysql_query(
            """
            SELECT r.record_id, r.record_type, r.description, r.due_date, r.status, u.full_name AS patient_name
            FROM followup_records r
            JOIN users u ON r.patient_id = u.user_id
            ORDER BY u.full_name ASC, r.due_date ASC
            """,
            fetchall=True
        )
        
        if not records:
            print("No patient follow-up entries exist in the database.")
            return
            
        current_patient = None
        for r in records:
            if r["patient_name"] != current_patient:
                current_patient = r["patient_name"]
                print(f"\nPatient: {current_patient.upper()}")
                print("=" * 40)
                
            due_str = r["due_date"].strftime("%Y-%m-%d") if hasattr(r["due_date"], "strftime") else str(r["due_date"])
            status_text = r["status"].upper()
            if r["status"] == "overdue":
                status_text = f"\033[91m{status_text} ⚠️\033[0m"
            elif r["status"] == "completed":
                status_text = f"\033[92m{status_text} ✓\033[0m"
                
            print(f"  [{r['record_type'].upper()}] ID: {r['record_id']} | Due: {due_str} | Status: {status_text}")
            print(f"  Description: {r['description']}")
            print("  " + "-" * 30)
    except Exception as e:
        print(f"Error loading compliance sheet: {e}")

# Updated by grace1513

# Updated by grace1513
