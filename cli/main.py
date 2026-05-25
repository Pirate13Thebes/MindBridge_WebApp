import sys
from pathlib import Path

# Add project root to sys.path to resolve standard folder imports
sys.path.append(str(Path(__file__).resolve().parent.parent))

from db.mysql_db import init_mysql_db
from db.mongo_db import init_mongo_db
from cli.auth import register_user_cli, login_user_cli
from cli import reminders, therapy, followup, education, support, exercise, journal, admin

def boot_databases():
    """Attempt database schema migrations and indexing on launch."""
    print("==================================================")
    print("       INITIALIZING MINDBRIDGE PLATFORM...")
    print("==================================================")
    try:
        init_mysql_db()
    except Exception as e:
        print(f"Warning: Could not connect to local MySQL on launch: {e}")
        
    try:
        init_mongo_db()
    except Exception as e:
        print(f"Warning: Could not connect to local MongoDB on launch: {e}")
    print("==================================================\n")

def run_role_menu(session):
    """Present role-restricted features in a loop until logout."""
    role = session["role"]
    username = session["username"]
    full_name = session["full_name"]
    
    while True:
        print(f"\n==================================================")
        print(f"  MINDBRIDGE DASHBOARD | User: {username} ({role.upper()})")
        print(f"==================================================")
        
        if role == "patient":
            print("[1] Therapy Sessions (Book, View, Cancel)")
            print("[2] Care Follow-up Tracker (Medications, Checkups)")
            print("[3] Educational Library (Browse, Search)")
            print("[4] Support Resources (Peer Groups, Hotlines)")
            print("[5] Stage Recovery Exercises (Pregnancy/Postnatal)")
            print("[6] Confidential Mood Journal (Write, View History)")
            print("[0] Logout and Exit to Main Menu")
        elif role == "provider":
            print("[1] Therapy Sessions (Client Roster, Complete, Cancel)")
            print("[2] Client Care Follow-up Compliance Overview")
            print("[3] Educational Library (Browse Articles)")
            print("[0] Logout and Exit to Main Menu")
        elif role == "admin":
            print("[1] Admin Controls (System Stats, User Directory, CSV Export)")
            print("[2] All Therapy Sessions (Roster View)")
            print("[3] Educational Library Management (Admin CRUD)")
            print("[4] Support Directory Management (Admin CRUD)")
            print("[0] Logout and Exit to Main Menu")
        elif role in ["volunteer", "family"]:
            print("[1] Educational Articles Library")
            print("[2] Professional & Peer Directory")
            print("[3] Stage Recovery Workouts")
            print("[0] Logout and Exit to Main Menu")
            
        choice = input("Select an option: ").strip()
        if choice == "0":
            print(f"\nLogging out session for {full_name}...")
            break
            
        # Feature Routing
        if role == "patient":
            if choice == "1":
                therapy.run(session)
            elif choice == "2":
                followup.run(session)
            elif choice == "3":
                education.run(session)
            elif choice == "4":
                support.run(session)
            elif choice == "5":
                exercise.run(session)
            elif choice == "6":
                journal.run(session)
            else:
                print("Invalid choice. Please select again.")
                
        elif role == "provider":
            if choice == "1":
                therapy.run(session)
            elif choice == "2":
                followup.run(session)
            elif choice == "3":
                education.run(session)
            else:
                print("Invalid choice. Please select again.")
                
        elif role == "admin":
            if choice == "1":
                admin.run(session)
            elif choice == "2":
                therapy.run(session)
            elif choice == "3":
                education.run(session)
            elif choice == "4":
                support.run(session)
            else:
                print("Invalid choice. Please select again.")
                
        elif role in ["volunteer", "family"]:
            if choice == "1":
                education.run(session)
            elif choice == choice == "2":
                support.run(session)
            elif choice == "3":
                exercise.run(session)
            else:
                print("Invalid choice. Please select again.")

def main():
    """Boots the dual-database setup and shows public menus."""
    boot_databases()
    
    while True:
        print("\n" + "="*50)
        print("          WELCOME TO MINDBRIDGE PPD CARE")
        print("  Empowering Mothers & Clinical Teams in Recovery")
        print("="*50)
        print("[1] Login to Account")
        print("[2] Register New Account")
        print("[0] Terminate Application")
        print("="*50)
        
        choice = input("Select option (0-2): ").strip()
        
        if choice == "0":
            print("\nShutting down MindBridge. Wishing you health and peace!")
            sys.exit(0)
        elif choice == "1":
            session = login_user_cli()
            if session:
                # Trigger Login Reminders Engine
                reminders.show_reminders(session)
                # Redirect to Dashboard Loop
                run_role_menu(session)
        elif choice == "2":
            register_user_cli()
        else:
            print("Invalid command. Please select 0, 1, or 2.")

if __name__ == "__main__":
    main()

# Updated by grace1513
