from db.mysql_db import execute_mysql_query
from db.mongo_db import get_mongo_db
from utils.exporter import generate_patient_csv
import os

def run(session):
    """Entry point for Admin module."""
    if session["role"] != "admin":
        print("Access Denied: Administrative controls are restricted.")
        return
        
    while True:
        print("\n=== System Administration Dashboard ===")
        print("[1] View System Performance & Statistics")
        print("[2] Browse User Directory")
        print("[3] Export Patient Profile History (CSV)")
        print("[0] Return to Main Menu")

        choice = input("Enter choice: ").strip()
        if choice == "0":
            break
            
        if choice == "1":
            view_system_statistics()
        elif choice == choice == "2":
            browse_user_directory()
        elif choice == "3":
            export_patient_csv_cli()

def view_system_statistics():
    """Display aggregate statistics across both relational and document databases."""
    print("\n--- System Performance & Database Statistics ---")
    try:
        # Relational statistics
        users_count = execute_mysql_query("SELECT COUNT(*) AS c FROM users", fetchone=True)["c"]
        sessions_count = execute_mysql_query("SELECT COUNT(*) AS c FROM therapy_sessions", fetchone=True)["c"]
        followups_count = execute_mysql_query("SELECT COUNT(*) AS c FROM followup_records", fetchone=True)["c"]
        articles_count = execute_mysql_query("SELECT COUNT(*) AS c FROM articles", fetchone=True)["c"]
        
        # Document store statistics
        db = get_mongo_db()
        journals_count = db.journal_entries.count_documents({})
        exercises_count = db.exercises.count_documents({})
        support_count = db.support_resources.count_documents({})
        
        print("\nStructured Data Metrics (MySQL Relational DB):")
        print(f"  • Total Registered System Users:       {users_count}")
        print(f"  • Total Clinical Appointments:         {sessions_count}")
        print(f"  • Total Post-natal Follow-up Checkups: {followups_count}")
        print(f"  • Total Psychoeducational Articles:    {articles_count}")
        
        print("\nFlexible Unstructured Metrics (MongoDB Document DB):")
        print(f"  • Total Confidential Mood Journals:    {journals_count}")
        print(f"  • Total Stage Recovery Exercises:      {exercises_count}")
        print(f"  • Total Support Support Listings:      {support_count}")
        print("-" * 50)
        
    except Exception as e:
        print(f"Database Stats Offline Fallback: {e}")
        print("\n[Simulated Sandbox Stats]:")
        print("  • Total Users: 14 | Total Clinical Appointments: 28 | Total Journals: 32")

def browse_user_directory():
    """List all registered system users."""
    print("\n--- Browse User Directory ---")
    try:
        users = execute_mysql_query("SELECT user_id, username, role, full_name, created_at FROM users ORDER BY user_id ASC", fetchall=True)
        if not users:
            print("No users are currently registered in the database.")
            return
            
        print(f"ID  | Username             | Role            | Full Name")
        print("-" * 70)
        for u in users:
            print(f"{u['user_id']:<3} | {u['username']:<20} | {u['role']:<15} | {u['full_name']}")
    except Exception as e:
        print(f"Error loading directory: {e}")

def export_patient_csv_cli():
    """Trigger the export utility for a specific patient."""
    print("\n--- Export Patient Profile CSV ---")
    try:
        # Prompt for patient list to make it user friendly
        patients = execute_mysql_query("SELECT user_id, username, full_name FROM users WHERE role = 'patient'", fetchall=True)
        if patients:
            print("Registered Patients:")
            for p in patients:
                print(f"  [{p['user_id']}] - {p['username']} ({p['full_name']})")
        else:
            print("No registered patients found in MySQL.")
            
        p_id_str = input("\nEnter Patient ID to export: ").strip()
        try:
            patient_id = int(p_id_str)
        except ValueError:
            print("Error: Invalid Patient ID format.")
            return
            
        # Execute CSV generator
        csv_data = generate_patient_csv(patient_id)
        if csv_data.startswith("Error"):
            print(csv_data)
            return
            
        filename = f"patient_{patient_id}_profile_export.csv"
        # Save to workspace root
        filepath = os.path.join(".", filename)
        
        with open(filepath, "w", newline="", encoding="utf-8") as f:
            f.write(csv_data)
            
        print(f"\nSuccess: Full relational & document logs for Patient ID {patient_id} compiled successfully!")
        print(f"File exported to workspace root: {os.path.abspath(filepath)}")
        
    except Exception as e:
        print(f"Error exporting data: {e}")

# Updated by sampsonfoli16

# Updated by sampsonfoli16
