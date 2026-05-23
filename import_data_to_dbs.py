import csv
import os
import datetime
from pathlib import Path
# pyrefly: ignore [missing-import]
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Import connection managers
from db.mysql_db import get_mysql_conn, init_mysql_db
from db.mongo_db import get_mongo_db, init_mongo_db

def run_live_import():
    """Import all 20,000 shuffled records from dummy_export_20000.csv into live MySQL and MongoDB."""
    print("====================================================")
    print("      MINDBRIDGE DUAL-DATABASE LIVE IMPORT TOOL     ")
    print("====================================================")
    
    # 1. Initialize MySQL tables and MongoDB indexes/collections
    print("\n[1/4] Initializing database schemas...")
    try:
        init_mysql_db()
        init_mongo_db()
        print("[OK] MySQL tables and MongoDB collections initialized successfully.")
    except Exception as e:
        print(f"[ERROR] Initialization Failed: {e}")
        print("Please ensure your local MySQL (3306) and MongoDB (27017) services are started and running.")
        return
        
    csv_path = Path("c:/Users/DELL/Downloads/MindBridge_WebApp/dummy_export_20000.csv")
    if not csv_path.exists():
        print(f"[ERROR] Compiled CSV file not found at: {csv_path}")
        return

    print(f"\n[2/4] Parsing unique patient identities from {csv_path.name}...")
    unique_users = {}
    
    with open(csv_path, "r", encoding="utf-8") as f:
        reader = csv.reader(f)
        header = next(reader)
        for row in reader:
            if not row:
                continue
            p_id = int(row[0])
            username = row[1]
            full_name = row[2]
            if p_id not in unique_users:
                unique_users[p_id] = {
                    "username": username,
                    "full_name": full_name
                }
                
    print(f"[OK] Found {len(unique_users)} unique patient profiles to register.")

    # 2. Establish connections
    mysql_conn = get_mysql_conn()
    mysql_cursor = mysql_conn.cursor()
    mongo_db = get_mongo_db()
    
    # 3. Seed users table in MySQL RDBMS
    print("\n[3/4] Registering patient profiles in MySQL 'users' table...")
    user_insert_query = """
        INSERT IGNORE INTO users (user_id, username, password_hash, role, full_name)
        VALUES (%s, %s, %s, %s, %s)
    """
    
    # Secure dummy Bcrypt hash safe for local offline presentations
    dummy_password_hash = "$2b$12$DummyBcryptHashSafePlaceholderForPasswordCheck123"
    
    user_batch = []
    for uid, udata in unique_users.items():
        user_batch.append((uid, udata["username"], dummy_password_hash, "patient", udata["full_name"]))
        
    mysql_cursor.executemany(user_insert_query, user_batch)
    mysql_conn.commit()
    print("[OK] Patients registered successfully.")

    # Seed default Doctor/Therapist provider account in users table
    doc_id = 9999
    mysql_cursor.execute("""
        INSERT IGNORE INTO users (user_id, username, password_hash, role, full_name)
        VALUES (%s, 'dr_sarah', %s, 'provider', 'Dr. Sarah Jenkins')
    """, (doc_id, dummy_password_hash))
    mysql_conn.commit()
    print("[OK] Therapist provider registered successfully.")

    # 4. Stream care records to live SQL tables and MongoDB document collection
    print("\n[4/4] Streaming 20,000 care records to live databases...")
    
    session_insert_query = """
        INSERT INTO therapy_sessions (patient_id, therapist_id, session_date, notes, status)
        VALUES (%s, %s, %s, %s, %s)
    """
    
    followup_insert_query = """
        INSERT INTO followup_records (patient_id, record_type, description, due_date, status)
        VALUES (%s, %s, %s, %s, %s)
    """
    
    mongo_journals = []
    mysql_sessions = []
    mysql_followups = []
    
    with open(csv_path, "r", encoding="utf-8") as f:
        reader = csv.reader(f)
        next(reader)  # Skip header
        
        for row in reader:
            if not row:
                continue
            p_id = int(row[0])
            data_type = row[3]
            record_id = row[4]
            date_val = row[5]
            label = row[6]
            status = row[7]
            description = row[8]
            
            if data_type == "Therapy Session":
                mysql_sessions.append((p_id, doc_id, date_val, description, status))
                
            elif data_type == "Follow-up Task":
                mysql_followups.append((p_id, label, description, date_val, status))
                
            elif data_type == "Mood Journal Entry":
                try:
                    dt = datetime.datetime.strptime(date_val, "%Y-%m-%d %H:%M:%S")
                except ValueError:
                    dt = datetime.datetime.now()
                mongo_journals.append({
                    "patient_id": p_id,
                    "content": description,
                    "mood": status,
                    "created_at": dt
                })
                
            # Perform regular batch insertions to maintain low memory footprints
            if len(mysql_sessions) >= 1000:
                mysql_cursor.executemany(session_insert_query, mysql_sessions)
                mysql_conn.commit()
                mysql_sessions = []
                
            if len(mysql_followups) >= 1000:
                mysql_cursor.executemany(followup_insert_query, mysql_followups)
                mysql_conn.commit()
                mysql_followups = []
                
            if len(mongo_journals) >= 1000:
                mongo_db.journal_entries.insert_many(mongo_journals)
                mongo_journals = []

        # Flush any remaining items in buffers
        if mysql_sessions:
            mysql_cursor.executemany(session_insert_query, mysql_sessions)
            mysql_conn.commit()
        if mysql_followups:
            mysql_cursor.executemany(followup_insert_query, mysql_followups)
            mysql_conn.commit()
        if mongo_journals:
            mongo_db.journal_entries.insert_many(mongo_journals)

    mysql_cursor.close()
    mysql_conn.close()
    
    print("\n====================================================")
    print("[SUCCESS] All 20,000 shuffled records successfully ")
    print("   imported into your live MySQL & MongoDB databases!")
    print("====================================================")

if __name__ == "__main__":
    run_live_import()
