from flask import Blueprint, request, jsonify, g
from db.mongo_db import get_mongo_db
from api.middleware import token_required, admin_required

support_bp = Blueprint("support_bp", __name__)

@support_bp.route("", methods=["GET"])
@token_required
def get_support_resources():
    """Retrieve professional and peer support directories from MongoDB."""
    category = request.args.get("category", "").strip()
    
    try:
        db = get_mongo_db()
        query_filter = {}
        if category:
            query_filter = {"category": category}
            
        resources = list(db.support_resources.find(query_filter))
        
        # Serialize MongoDB ObjectId to string
        for r in resources:
            r["_id"] = str(r["_id"])
            
        return jsonify(resources), 200
    except Exception as e:
        print(f"[Demo Mode Fallback] Support resources database failed: {e}")
        from db.mock_db import MOCK_SUPPORT_RESOURCES
        import copy
        resources = copy.deepcopy(MOCK_SUPPORT_RESOURCES)
        if category:
            resources = [r for r in resources if r["category"] == category]
        for idx, r in enumerate(resources):
            r["_id"] = f"MOCK_SUP_{idx}"
        return jsonify(resources), 200

@support_bp.route("", methods=["POST"])
@token_required
@admin_required
def create_support_resource():
    """Create a new support directory entry in MongoDB (Admin only)."""
    data = request.get_json() or {}
    name = data.get("name", "").strip()
    category = data.get("category", "").strip()
    contact = data.get("contact", "").strip()
    description = data.get("description", "").strip()
    
    if not name or not contact or category not in ["peer", "counselor", "hotline"]:
        return jsonify({"message": "Name, contact, and valid category (peer, counselor, hotline) are required."}), 400
        
    try:
        db = get_mongo_db()
        result = db.support_resources.insert_one({
            "name": name,
            "category": category,
            "contact": contact,
            "description": description
        })
        return jsonify({"message": "Support listing saved!", "id": str(result.inserted_id)}), 201
    except Exception as e:
        print(f"[Demo Mode Fallback] Create support resource database failed: {e}")
        from db.mock_db import MOCK_SUPPORT_RESOURCES
        new_resource = {
            "name": name,
            "category": category,
            "contact": contact,
            "description": description
        }
        MOCK_SUPPORT_RESOURCES.append(new_resource)
        return jsonify({"message": "Support listing saved (Offline Demo Mode)!", "id": "MOCK_SUP_NEW"}), 201
