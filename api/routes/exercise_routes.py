from flask import Blueprint, request, jsonify
from db.mongo_db import get_mongo_db
from api.middleware import token_required

exercise_bp = Blueprint("exercise_bp", __name__)

@exercise_bp.route("", methods=["GET"])
@token_required
def get_exercises():
    """Retrieve physical recovery exercise modules from MongoDB by maternal stage."""
    stage = request.args.get("stage", "").strip()
    
    try:
        db = get_mongo_db()
        query_filter = {}
        if stage:
            query_filter = {"stage": stage}
            
        exercises = list(db.exercises.find(query_filter))
        
        # Serialize ObjectId to string
        for ex in exercises:
            ex["_id"] = str(ex["_id"])
            
        return jsonify(exercises), 200
    except Exception as e:
        print(f"[Demo Mode Fallback] Exercise database failed: {e}")
        from db.mock_db import MOCK_EXERCISES
        import copy
        exercises = copy.deepcopy(MOCK_EXERCISES)
        if stage:
            exercises = [ex for ex in exercises if ex["stage"] == stage]
        for idx, ex in enumerate(exercises):
            ex["_id"] = f"MOCK_EX_{idx}"
        return jsonify(exercises), 200
