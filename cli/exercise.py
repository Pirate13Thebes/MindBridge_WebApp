from db.mongo_db import get_mongo_db

def run(session):
    """Entry point for Exercise guidance module."""
    while True:
        print("\n=== Maternal Physical Recovery & Exercise Guidelines ===")
        print("Select Maternal Stage:")
        print("[1] Trimester 1 (Weeks 1 - 12)")
        print("[2] Trimester 2 (Weeks 13 - 26)")
        print("[3] Trimester 3 (Weeks 27 - 40)")
        print("[4] Postpartum Early Recovery (0 - 6 Weeks Postnatal)")
        print("[5] Postpartum Late Strength (6+ Weeks Postnatal)")
        print("[0] Return to Main Menu")

        choice = input("Enter choice (0-5): ").strip()
        if choice == "0":
            break
            
        stage = None
        if choice == "1":
            stage = "trimester_1"
        elif choice == "2":
            stage = "trimester_2"
        elif choice == "3":
            stage = "trimester_3"
        elif choice == "4":
            stage = "postpartum_early"
        elif choice == "5":
            stage = "postpartum_late"
            
        if stage:
            view_exercises_by_stage(stage)

def view_exercises_by_stage(stage):
    """Query MongoDB to fetch recommended exercises for selected maternal stage."""
    stage_names = {
        "trimester_1": "Trimester 1",
        "trimester_2": "Trimester 2",
        "trimester_3": "Trimester 3",
        "postpartum_early": "Postpartum Early Recovery",
        "postpartum_late": "Postpartum Late Strength"
    }
    
    print(f"\n--- Recommended Exercises: {stage_names[stage]} ---")
    try:
        db = get_mongo_db()
        # Query matching stage using PyMongo filter
        exercises = list(db.exercises.find({"stage": stage}))
        
        if not exercises:
            print("No guidelines have been uploaded for this maternal stage yet.")
            return
            
        for i, ex in enumerate(exercises, 1):
            print(f"{i}. {ex['name']} ({ex['duration_min']} mins)")
            print(f"   Description: {ex['description']}")
            print("-" * 50)
            
    except Exception as e:
        print(f"MongoDB Offline Fallback Mode: {e}")
        # Static mock fallback
        if stage == "postpartum_early":
            print("1. Pelvic Floor Restorative Contractions (5 mins)")
            print("   Description: Low intensity Kegels and transverse abdominis activations.")
            print("2. Postpartum Rebalancing Walk (15 mins)")
            print("   Description: Light walking around the neighborhood with erect posture.")
        else:
            print("1. Diaphragmatic Deep Breathing (10 mins)")
            print("   Description: Focus on lung expansion, stress relief, and abdominal contraction.")
