from db.mongo_db import get_mongo_db
from bson import ObjectId

def run(session):
    """Entry point for Support resources module."""
    role = session["role"]
    
    while True:
        print("\n=== Professional & Peer Support Directories ===")
        print("[1] Browse Support Resources")
        if role == "admin":
            print("[2] Add Support Resource (Admin Only)")
            print("[3] Delete Support Resource (Admin Only)")
        print("[0] Return to Main Menu")

        choice = input("Enter choice: ").strip()
        if choice == "0":
            break
            
        if choice == "1":
            browse_support()
        elif choice == "2" and role == "admin":
            add_support_admin()
        elif choice == "3" and role == "admin":
            delete_support_admin()

def browse_support():
    """Browse support resources by category."""
    print("\n--- Browse Directory ---")
    print("Select Category:")
    print("[1] Peer Support Networks")
    print("[2] Certified Professional Counselors")
    print("[3] Emergency 24/7 Hotlines")
    print("[4] View All")
    
    choice = input("Enter choice (1-4): ").strip()
    category = None
    if choice == "1":
        category = "peer"
    elif choice == "2":
        category = "counselor"
    elif choice == "3":
        category = "hotline"
        
    try:
        db = get_mongo_db()
        query_filter = {}
        if category:
            query_filter = {"category": category}
            
        resources = list(db.support_resources.find(query_filter))
        
        if not resources:
            print("No matching support directories exist in this category.")
            return
            
        print(f"\nFound {len(resources)} listings:")
        print("=" * 60)
        for r in resources:
            cat_label = r["category"].upper()
            print(f"ID: {r['_id']} | Category: [{cat_label}]")
            print(f"Name: {r['name']}")
            print(f"Contact: {r['contact']}")
            print(f"Description: {r['description']}")
            print("-" * 60)
            
    except Exception as e:
        print(f"MongoDB Offline Fallback Mode: {e}")
        # Simulating standard offline fallback
        print("\n[Simulated Directories]:")
        print("1. National Maternal Mental Health Hotline (Category: Hotline) - Contact: 1-833-TLC-MAMA")
        print("2. Postpartum Support International (Category: Peer Support) - Contact: postpartum.net")

def add_support_admin():
    """Admin adds support resource directly to MongoDB."""
    print("\n--- Add Support Directory (Admin Console) ---")
    name = input("Resource/Provider Name: ").strip()
    if not name:
        print("Error: Name cannot be empty.")
        return
        
    print("Category Type:")
    print("[1] Peer Network")
    print("[2] Counselor")
    print("[3] Hotline")
    cat_choice = input("Select Option (1-3): ").strip()
    
    category = "peer"
    if cat_choice == "2":
        category = "counselor"
    elif cat_choice == "3":
        category = "hotline"
        
    contact = input("Contact Details (phone, email, web): ").strip()
    if not contact:
        print("Error: Contact details cannot be empty.")
        return
        
    description = input("Resource Description: ").strip()
    
    try:
        db = get_mongo_db()
        db.support_resources.insert_one({
            "name": name,
            "category": category,
            "contact": contact,
            "description": description
        })
        print("\nSuccess: Support resource added to MongoDB.")
    except Exception as e:
        print(f"Error writing to MongoDB: {e}")

def delete_support_admin():
    """Admin deletes support resource by ID."""
    print("\n--- Remove Support Resource ---")
    res_id_str = input("Enter Resource MongoDB ID: ").strip()
    
    try:
        db = get_mongo_db()
        # MongoDB operations use PyMongo dict filters (no raw string injection)
        result = db.support_resources.delete_one({"_id": ObjectId(res_id_str)})
        if result.deleted_count > 0:
            print("Success: Support listing removed from MongoDB.")
        else:
            print("Error: Listing not found.")
    except Exception as e:
        print(f"Error deleting from MongoDB: {e}. (Ensure ID format is a valid 24-character hexadecimal string)")
