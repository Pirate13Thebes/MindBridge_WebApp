import datetime
import bcrypt

# Centralized in-memory fallback databases for offline presentation mode
MOCK_USERS = [
    {
        "user_id": 1, 
        "username": "patient", 
        # bcrypt hash of 'password123'
        "password_hash": "$2b$12$DummyBcryptHashSafePlaceholderForPasswordCheck123", 
        "role": "patient", 
        "full_name": "Jane Doe",
        "created_at": "2026-05-22T20:00:00"
    },
    {
        "user_id": 2, 
        "username": "provider", 
        "password_hash": "$2b$12$DummyBcryptHashSafePlaceholderForPasswordCheck123", 
        "role": "provider", 
        "full_name": "Dr. Sarah Jenkins",
        "created_at": "2026-05-22T20:00:00"
    },
    {
        "user_id": 3, 
        "username": "admin", 
        "password_hash": "$2b$12$DummyBcryptHashSafePlaceholderForPasswordCheck123", 
        "role": "admin", 
        "full_name": "System Administrator",
        "created_at": "2026-05-22T20:00:00"
    }
]

MOCK_THERAPY_SESSIONS = [
    {
        "session_id": 1,
        "patient_id": 1,
        "therapist_id": 2,
        "session_date": "2026-05-25",
        "notes": "Discussed early fatigue symptoms and transition back to daily routines.",
        "status": "scheduled"
    },
    {
        "session_id": 2,
        "patient_id": 1,
        "therapist_id": 2,
        "session_date": "2026-05-18",
        "notes": "Initial consultation completed. Patient displays good progressive resilience.",
        "status": "completed"
    }
]

MOCK_FOLLOWUP_RECORDS = [
    {
        "record_id": 1,
        "patient_id": 1,
        "record_type": "medication",
        "description": "Daily post-natal vitamins and iron supplements compliance check.",
        "due_date": "2026-05-24",
        "status": "pending"
    },
    {
        "record_id": 2,
        "patient_id": 1,
        "record_type": "checkup",
        "description": "6-week pelvic floor tone and recovery milestone clinic checkup.",
        "due_date": "2026-05-20",
        "status": "completed"
    },
    {
        "record_id": 3,
        "patient_id": 1,
        "record_type": "injection",
        "description": "Routine blood count parameter tracking check.",
        "due_date": "2026-05-10",
        "status": "overdue"
    }
]

MOCK_JOURNALS = [
    {
        "patient_id": 1,
        "content": "Today felt like a good step forward. Spent some time with the newborn outside.",
        "mood": "good",
        "created_at": "2026-05-22T14:30:00"
    },
    {
        "patient_id": 1,
        "content": "Feeling slightly fatigued but remaining optimistic. Practice deep breathing exercises.",
        "mood": "okay",
        "created_at": "2026-05-21T09:15:00"
    }
]

MOCK_EXERCISES = [
    {
        "name": "Pelvic Floor Restorative Contractions",
        "stage": "postpartum_early",
        "description": "Gentle, low-intensity contractions and transverse activations to recover tissue elasticity.",
        "duration_min": 5
    },
    {
        "name": "Postpartum Rebalancing Walk",
        "stage": "postpartum_early",
        "description": "Light walking around the neighborhood with erect posture to re-acclimate the body.",
        "duration_min": 15
    },
    {
        "name": "Core Strengthening (Dead Bugs)",
        "stage": "postpartum_late",
        "description": "Safe, non-crunches abdominal stabilization exercises to repair rectus diastasis safely.",
        "duration_min": 12
    },
    {
        "name": "Gentle Morning Stretching",
        "stage": "trimester_1",
        "description": "Slow neck rolls, shoulder rolls, and side stretches to alleviate early pregnancy fatigue.",
        "duration_min": 10
    },
    {
        "name": "Diaphragmatic Breathing",
        "stage": "trimester_3",
        "description": "Controlled deep belly breathing techniques to expand lung capacity and lower stress levels.",
        "duration_min": 10
    }
]

MOCK_SUPPORT_RESOURCES = [
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
        "description": "Provides local coordinators, online support groups, and peer resources."
    },
    {
        "name": "Dr. Sarah Jenkins (PPD Counselor)",
        "category": "counselor",
        "contact": "555-019-2834 / s.jenkins@mindbridge.com",
        "description": "Licensed clinical psychologist specializing in postpartum recovery transitions."
    }
]

MOCK_ARTICLES = [
    {
        "article_id": 1,
        "title": "Understanding Postpartum Baby Blues vs Depression",
        "body": "Many mothers experience mood swings and fatigue (baby blues) after birth, but persistent symptoms of deep hopelessness suggest PPD. Seek self-care, counseling support, and structured recovery exercises.",
        "topic": "education"
    },
    {
        "article_id": 2,
        "title": "Self-Care Guidelines for Modern Postnatal Recovery",
        "body": "Optimal postnatal health requires balanced nutrition, pelvic stabilizers, deep diaphragmatic breathing routines, and open emotional communication. Active journaling and peer support hotlines build emotional resilience.",
        "topic": "self-care"
    }
]

# Helper logic functions
def register_mock_user(username, password_hash, role, full_name):
    for u in MOCK_USERS:
        if u["username"] == username:
            return False
    new_id = len(MOCK_USERS) + 1
    new_user = {
        "user_id": new_id,
        "username": username,
        "password_hash": password_hash,
        "role": role,
        "full_name": full_name,
        "created_at": datetime.datetime.now().isoformat()
    }
    MOCK_USERS.append(new_user)
    return new_user

def get_mock_user_by_username(username):
    for u in MOCK_USERS:
        if u["username"] == username:
            return u
    return None

def get_mock_user_by_id(user_id):
    for u in MOCK_USERS:
        if u["user_id"] == user_id:
            return u
    return None

def get_mock_users():
    return MOCK_USERS

def get_mock_stats():
    return {
        "users": len(MOCK_USERS),
        "therapy_sessions": len(MOCK_THERAPY_SESSIONS),
        "followup_records": len(MOCK_FOLLOWUP_RECORDS),
        "articles": len(MOCK_ARTICLES),
        "journals": len(MOCK_JOURNALS),
        "exercises": len(MOCK_EXERCISES),
        "support_resources": len(MOCK_SUPPORT_RESOURCES)
    }
