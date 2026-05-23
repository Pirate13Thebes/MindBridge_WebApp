from flask import Blueprint, request, jsonify, g
from db.mysql_db import execute_mysql_query
from api.middleware import token_required, admin_required

education_bp = Blueprint("education_bp", __name__)

@education_bp.route("", methods=["GET"])
@token_required
def get_articles():
    """Retrieve educational articles, supporting optional keyword search query."""
    query = request.args.get("q", "").strip()
    
    try:
        if query:
            # 1. Try FULLTEXT Match
            articles = execute_mysql_query(
                """
                SELECT a.article_id, a.title, a.body, a.topic, a.created_at, u.full_name AS author_name,
                       MATCH(a.title, a.body) AGAINST(%s IN NATURAL LANGUAGE MODE) AS score
                FROM articles a
                LEFT JOIN users u ON a.author_id = u.user_id
                WHERE MATCH(a.title, a.body) AGAINST(%s IN NATURAL LANGUAGE MODE) > 0
                ORDER BY score DESC
                """,
                (query, query),
                fetchall=True
            )
            
            if not articles:
                # 2. Fallback to LIKE wildcard matching
                like_query = f"%{query}%"
                articles = execute_mysql_query(
                    """
                    SELECT a.article_id, a.title, a.body, a.topic, a.created_at, u.full_name AS author_name
                    FROM articles a
                    LEFT JOIN users u ON a.author_id = u.user_id
                    WHERE a.title LIKE %s OR a.body LIKE %s OR a.topic LIKE %s
                    ORDER BY a.created_at DESC
                    """,
                    (like_query, like_query, like_query),
                    fetchall=True
                )
        else:
            # Standard listing
            articles = execute_mysql_query(
                """
                SELECT a.article_id, a.title, a.body, a.topic, a.created_at, u.full_name AS author_name
                FROM articles a
                LEFT JOIN users u ON a.author_id = u.user_id
                ORDER BY a.created_at DESC
                """,
                fetchall=True
            )
            
        # Format date strings
        for a in articles:
            if hasattr(a["created_at"], "isoformat"):
                a["created_at"] = a["created_at"].isoformat()
            else:
                a["created_at"] = str(a["created_at"])
                
        return jsonify(articles), 200
    except Exception as e:
        print(f"[Demo Mode Fallback] Articles database failed: {e}")
        from db.mock_db import MOCK_ARTICLES
        import copy
        articles = copy.deepcopy(MOCK_ARTICLES)
        for a in articles:
            a["author_name"] = "Dr. Sarah Jenkins"
            a["created_at"] = "2026-05-22T20:00:00"
        if query:
            q_lower = query.lower()
            articles = [
                a for a in articles 
                if q_lower in a["title"].lower() or q_lower in a["body"].lower() or q_lower in a.get("topic", "").lower()
            ]
        return jsonify(articles), 200

@education_bp.route("", methods=["POST"])
@token_required
@admin_required
def create_article():
    """Publish a new psychoeducational article (Admin only)."""
    user = g.user
    data = request.get_json() or {}
    title = data.get("title", "").strip()
    body = data.get("body", "").strip()
    topic = data.get("topic", "").strip()
    
    if not title or not body or not topic:
        return jsonify({"message": "Title, topic, and body are required."}), 400
        
    try:
        execute_mysql_query(
            "INSERT INTO articles (title, body, topic, author_id) VALUES (%s, %s, %s, %s)",
            (title, body, topic, user["user_id"]),
            commit=True
        )
        return jsonify({"message": "Article published successfully!"}), 201
    except Exception as e:
        print(f"[Demo Mode Fallback] Create article database failed: {e}")
        from db.mock_db import MOCK_ARTICLES
        new_id = len(MOCK_ARTICLES) + 1
        new_article = {
            "article_id": new_id,
            "title": title,
            "body": body,
            "topic": topic,
            "author_id": int(user["user_id"]),
            "author_name": user["full_name"],
            "created_at": "2026-05-22T20:00:00"
        }
        MOCK_ARTICLES.append(new_article)
        return jsonify({"message": "Article published successfully (Offline Demo Mode)!"}), 201

@education_bp.route("/<int:article_id>", methods=["DELETE"])
@token_required
@admin_required
def delete_article(article_id):
    """Delete an article (Admin only)."""
    try:
        # Check if exists
        exists = execute_mysql_query("SELECT title FROM articles WHERE article_id = %s", (article_id,), fetchone=True)
        if not exists:
            return jsonify({"message": "Article not found."}), 404
            
        execute_mysql_query("DELETE FROM articles WHERE article_id = %s", (article_id,), commit=True)
        return jsonify({"message": "Article deleted successfully."}), 200
    except Exception as e:
        print(f"[Demo Mode Fallback] Delete article database failed: {e}")
        from db.mock_db import MOCK_ARTICLES
        for idx, a in enumerate(MOCK_ARTICLES):
            if a["article_id"] == article_id:
                MOCK_ARTICLES.pop(idx)
                break
        return jsonify({"message": "Article deleted successfully (Offline Demo Mode)."}), 200
