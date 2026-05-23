import os
import pymongo
from pymongo import MongoClient
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

_client = None

def get_mongo_client():
    """Establish and return MongoClient instance."""
    global _client
    if _client is None:
        mongo_uri = os.getenv("MONGO_URI", "mongodb://localhost:27017")
        # Initialize single connection client with a fast 2-second timeout for offline environments
        _client = MongoClient(mongo_uri, serverSelectionTimeoutMS=2000)
    return _client

def get_mongo_db():
    """Retrieve the pymongo database reference."""
    client = get_mongo_client()
    db_name = os.getenv("MONGO_DATABASE", "mindbridge")
    return client[db_name]

def init_mongo_db():
    """Initialize MongoDB: build indexes and seed exercises/support resources."""
    db = get_mongo_db()
    
    # 1. Build indexes
    db.journal_entries.create_index([("patient_id", pymongo.ASCENDING), ("created_at", pymongo.DESCENDING)])
    db.exercises.create_index([("stage", pymongo.ASCENDING)])
    db.support_resources.create_index([("category", pymongo.ASCENDING)])
    
    # 2. Seed exercises if empty
    if db.exercises.count_documents({}) == 0:
        exercises_seed = [
            # trimester_1
            {
                "name": "Gentle Morning Stretching",
                "stage": "trimester_1",
                "description": "Slow neck rolls, shoulder rolls, and side stretches to alleviate early pregnancy fatigue and physical stiffness.",
                "duration_min": 10
            },
            {
                "name": "Pelvic Tilts (Cat-Cow)",
                "stage": "trimester_1",
                "description": "Hands and knees pelvic rocking to maintain back flexibility and improve core alignment.",
                "duration_min": 12
            },
            # trimester_2
            {
                "name": "Prenatal Yoga Flow",
                "stage": "trimester_2",
                "description": "Safe warrior poses, tree posture, and deep breathing to build stamina and maintain hip opening.",
                "duration_min": 20
            },
            {
                "name": "Wall Squats",
                "stage": "trimester_2",
                "description": "Leaning back on a flat wall and lowering down to strengthen quadriceps and glutes for labor preparation.",
                "duration_min": 15
            },
            # trimester_3
            {
                "name": "Kegel Strengthening Exercises",
                "stage": "trimester_3",
                "description": "Focus on contracting and relaxing pelvic floor muscles to prepare for childbirth and reduce incontinence.",
                "duration_min": 8
            },
            {
                "name": "Diaphragmatic Breathing",
                "stage": "trimester_3",
                "description": "Controlled deep belly breathing techniques to expand lung capacity and lower blood pressure/stress levels.",
                "duration_min": 10
            },
            # postpartum_early
            {
                "name": "Pelvic Floor Restorative Contractions",
                "stage": "postpartum_early",
                "description": "Gentle, low-intensity Kegels and transverse abdominis activations to recover tissue elasticity and blood circulation.",
                "duration_min": 5
            },
            {
                "name": "Postpartum Rebalancing Walk",
                "stage": "postpartum_early",
                "description": "Light walking around the neighborhood with erect posture to re-acclimate the musculoskeletal system.",
                "duration_min": 15
            },
            # postpartum_late
            {
                "name": "Core Strengthening (Dead Bugs)",
                "stage": "postpartum_late",
                "description": "Safe, non-crunches abdominal stabilization exercises to repair rectus diastasis safely.",
                "duration_min": 12
            },
            {
                "name": "Low-Impact Cardio Flow",
                "stage": "postpartum_late",
                "description": "Moderate bodyweight movements, dynamic lunges, and active recovery routines for energy reclamation.",
                "duration_min": 25
            }
        ]
        db.exercises.insert_many(exercises_seed)
        print("MongoDB: Preloaded maternal recovery exercises seeded.")

    # 3. Seed some default support resources if empty
    if db.support_resources.count_documents({}) == 0:
        resources_seed = [
            {
                "name": "National Maternal Mental Health Hotline",
                "category": "hotline",
                "contact": "1-833-TLC-MAMA (1-833-852-6262)",
                "description": "24/7, free, confidential hotline for pregnant and postpartum individuals."
            },
            {
                "name": "Postpartum Support International (PSI)",
                "category": "peer",
                "contact": "https://www.postpartum.net",
                "description": "Provides local coordinators, online support meetings, and peer resources."
            },
            {
                "name": "Dr. Sarah Jenkins (PPD Counselor)",
                "category": "counselor",
                "contact": "555-019-2834 / s.jenkins@mindbridge.com",
                "description": "Licensed perinatal clinical psychologist specializing in postpartum transitions."
            }
        ]
        db.support_resources.insert_many(resources_seed)
        print("MongoDB: Support resources seeded.")

    print("MongoDB database initialization completed successfully.")
