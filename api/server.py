import os
import sys
from pathlib import Path

# Add project root to sys.path to resolve standard folder imports
sys.path.append(str(Path(__file__).resolve().parent.parent))

# pyrefly: ignore [missing-import]
from flask import Flask, jsonify
from flask_cors import CORS
# pyrefly: ignore [missing-import]
from dotenv import load_dotenv

# Database boots on startup
from db.mysql_db import init_mysql_db
from db.mongo_db import init_mongo_db

# Blueprint routers
from api.routes.auth_routes import auth_bp
from api.routes.therapy_routes import therapy_bp
from api.routes.education_routes import education_bp
from api.routes.followup_routes import followup_bp
from api.routes.support_routes import support_bp
from api.routes.exercise_routes import exercise_bp
from api.routes.journal_routes import journal_bp
from api.routes.admin_routes import admin_bp

load_dotenv()

app = Flask(__name__)

# Configure Secret Keys
app.config["SECRET_KEY"] = os.getenv("SECRET_KEY", "change-me-in-production")

# Enable Cross-Origin Resource Sharing (CORS) globally
CORS(app, resources={r"/api/*": {"origins": "*"}})

# Healthcheck probe
@app.route("/api/health", methods=["GET"])
def healthcheck():
    return jsonify({"status": "healthy", "service": "MindBridge API Server"}), 200

# Register Blueprints under standard prefix /api/v1
app.register_blueprint(auth_bp, url_prefix="/api/v1/auth")
app.register_blueprint(therapy_bp, url_prefix="/api/v1/therapy")
app.register_blueprint(education_bp, url_prefix="/api/v1/articles")
app.register_blueprint(followup_bp, url_prefix="/api/v1/followup")
app.register_blueprint(support_bp, url_prefix="/api/v1/support")
app.register_blueprint(exercise_bp, url_prefix="/api/v1/exercise")
app.register_blueprint(journal_bp, url_prefix="/api/v1/journal")

# Register admin_bp at the base /api/v1 so it can support both "/admin/stats" and "/dashboard/reminders" exactly
app.register_blueprint(admin_bp, url_prefix="/api/v1")

def start_server():
    """Initializes databases and spins up the Flask server."""
    print("==================================================")
    print("      LAUNCHING MINDBRIDGE API REST SERVER...")
    print("==================================================")
    
    # Run migrations/indexing
    try:
        init_mysql_db()
    except Exception as e:
        print(f"Warning: Could not init MySQL on server boot: {e}")
        
    try:
        init_mongo_db()
    except Exception as e:
        print(f"Warning: Could not init MongoDB on server boot: {e}")
        
    port = int(os.getenv("FLASK_PORT", 5000))
    # Run server
    app.run(host="0.0.0.0", port=port, debug=False)

if __name__ == "__main__":
    start_server()

# Updated by fkangira

# Updated by fkangira
