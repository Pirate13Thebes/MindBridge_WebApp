import datetime
from db.mongo_db import get_mongo_db

def run(session):
    """Entry point for Patient Journaling module."""
    if session["role"] != "patient":
        print("Access Denied: Mood journaling features are confidential and restricted to patients only.")
        return
        
    while True:
        print("\n=== Confidential Mood Journaling ===")
        print("[1] Write a New Journal Log")
        print("[2] Read My Journal History")
        print("[0] Return to Main Menu")

        choice = input("Enter choice: ").strip()
        if choice == "0":
            break
            
        if choice == "1":
            write_journal_entry(session)
        elif choice == "2":
            read_journal_history(session)

def write_journal_entry(session):
    """Patient writes a free-text journal entry with mood tracking."""
    print("\n--- Write Journal Entry ---")
    content = input("Type your thoughts/journal entry below:\n").strip()
    if not content:
        print("Error: Journal content cannot be empty.")
        return
        
    print("\nSelect your current emotional mood:")
    print("[1] Great (Highly energized, stable)")
    print("[2] Good (Happy, coping well)")
    print("[3] Okay (Average, moderate coping)")
    print("[4] Low (Sad, fatigued, low mood)")
    print("[5] Struggling (High anxiety, severe fatigue, overwhelmed)")
    
    mood_map = {
        "1": "great",
        "2": "good",
        "3": "okay",
        "4": "low",
        "5": "struggling"
    }
    
    while True:
        choice = input("Select Mood (1-5): ").strip()
        if choice in mood_map:
            mood = mood_map[choice]
            break
        print("Invalid choice. Select 1, 2, 3, 4, or 5.")
        
    try:
        db = get_mongo_db()
        db.journal_entries.insert_one({
            "patient_id": int(session["user_id"]),
            "content": content,
            "mood": mood,
            "created_at": datetime.datetime.now()
        })
        print("\nSuccess: Confidential journal log saved to MongoDB. Thank you for expressing yourself.")
    except Exception as e:
        print(f"Error saving journal to MongoDB: {e}")

def read_journal_history(session):
    """Retrieve and display patient's personal journal entries."""
    print("\n--- My Mood Journal History ---")
    try:
        db = get_mongo_db()
        # Find entries matching patient_id, sorted by created_at descending
        entries = list(db.journal_entries.find({"patient_id": int(session["user_id"])}).sort("created_at", -1))
        
        if not entries:
            print("Your mood journal is empty. Start writing to track your recovery path.")
            return
            
        for i, entry in enumerate(entries, 1):
            created = entry["created_at"]
            date_str = created.strftime("%Y-%m-%d %H:%M:%S") if hasattr(created, "strftime") else str(created)
            
            # Mood colors in CLI
            mood_labels = {
                "great": "\033[92mGREAT ✨\033[0m",
                "good": "\033[96mGOOD 🙂\033[0m",
                "okay": "\033[94mOKAY 😐\033[0m",
                "low": "\033[93mLOW 😔\033[0m",
                "struggling": "\033[91mSTRUGGLING ⚠️\033[0m"
            }
            mood_disp = mood_labels.get(entry["mood"], entry["mood"].upper())
            
            print(f"#{i} | Date: {date_str} | Mood: {mood_disp}")
            print(f"Content: {entry['content']}")
            print("=" * 60)
            
    except Exception as e:
        print(f"MongoDB Offline Fallback Mode: {e}")
        print("\n[Simulated History logs]:")
        print("1. 2026-05-22 12:00:00 | Mood: OKAY - Feeling slightly fatigued but staying positive.")


# Updated by grace1513

# Updated by grace1513
