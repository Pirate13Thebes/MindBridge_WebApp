import datetime
from flask import Blueprint, request, jsonify, g
from db.mongo_db import get_mongo_db
from api.middleware import token_required, patient_required

journal_bp = Blueprint("journal_bp", __name__)

@journal_bp.route("", methods=["GET"])
@token_required
@patient_required
def get_journal_entries():
    """Retrieve patient's mood journal entries from MongoDB (Patient only)."""
    user = g.user
    
    try:
        db = get_mongo_db()
        # MongoDB operations use PyMongo dict filters (no raw string injection)
        entries = list(db.journal_entries.find({"patient_id": int(user["user_id"])}).sort("created_at", -1))
        
        # Serialize ObjectID and datetime
        for entry in entries:
            entry["_id"] = str(entry["_id"])
            if hasattr(entry["created_at"], "isoformat"):
                entry["created_at"] = entry["created_at"].isoformat()
            else:
                entry["created_at"] = str(entry["created_at"])
                
        return jsonify(entries), 200
    except Exception as e:
        print(f"[Demo Mode Fallback] Journal database failed: {e}")
        from db.mock_db import MOCK_JOURNALS
        import copy
        entries = copy.deepcopy(MOCK_JOURNALS)
        # Filter entries for the current patient or show default mock journals
        user_entries = [e for e in entries if e["patient_id"] == int(user["user_id"])]
        if not user_entries:
            user_entries = entries  # Show defaults if none match
        for idx, entry in enumerate(user_entries):
            entry["_id"] = f"MOCK_J_{idx}"
        return jsonify(user_entries), 200

@journal_bp.route("", methods=["POST"])
@token_required
@patient_required
def create_journal_entry():
    """Submit a confidential mood journal log (Patient only)."""
    user = g.user
    data = request.get_json() or {}
    content = data.get("content", "").strip()
    mood = data.get("mood", "").strip()
    
    if not content or mood not in ["great", "good", "okay", "low", "struggling"]:
        return jsonify({"message": "Journal content and a valid mood level are required."}), 400
        
    try:
        db = get_mongo_db()
        result = db.journal_entries.insert_one({
            "patient_id": int(user["user_id"]),
            "content": content,
            "mood": mood,
            "created_at": datetime.datetime.now()
        })
        return jsonify({"message": "Confidential journal saved!", "id": str(result.inserted_id)}), 201
    except Exception as e:
        print(f"[Demo Mode Fallback] Journal insertion failed: {e}")
        from db.mock_db import MOCK_JOURNALS
        new_entry = {
            "patient_id": int(user["user_id"]),
            "content": content,
            "mood": mood,
            "created_at": datetime.datetime.now().isoformat()
        }
        MOCK_JOURNALS.insert(0, new_entry)
        return jsonify({"message": "Confidential journal saved (Offline Demo Mode)!", "id": "MOCK_J_NEW"}), 201
