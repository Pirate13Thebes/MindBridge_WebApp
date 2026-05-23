from db.mysql_db import execute_mysql_query

def run(session):
    """Entry point for Education articles module."""
    role = session["role"]
    
    while True:
        print("\n=== Educational Resource Hub ===")
        print("[1] Browse All Articles")
        print("[2] Search Articles by Keyword")
        if role == "admin":
            print("[3] Publish New Article (Admin Only)")
            print("[4] Delete an Article (Admin Only)")
        print("[0] Return to Main Menu")

        choice = input("Enter choice: ").strip()
        if choice == "0":
            break
            
        if choice == "1":
            browse_articles()
        elif choice == "2":
            search_articles()
        elif choice == "3" and role == "admin":
            publish_article_admin(session)
        elif choice == "4" and role == "admin":
            delete_article_admin()

def browse_articles():
    """List all psychoeducational articles in the system."""
    print("\n--- Browse Articles ---")
    try:
        articles = execute_mysql_query(
            """
            SELECT a.article_id, a.title, a.topic, a.created_at, u.full_name AS author_name
            FROM articles a
            LEFT JOIN users u ON a.author_id = u.user_id
            ORDER BY a.created_at DESC
            """,
            fetchall=True
        )
        
        if not articles:
            print("No educational articles found. Check back soon!")
            return
            
        for a in articles:
            date_str = a["created_at"].strftime("%Y-%m-%d") if hasattr(a["created_at"], "strftime") else str(a["created_at"])
            print(f"ID: {a['article_id']} | [{a['topic'].upper()}] - {a['title']}")
            print(f"  Published: {date_str} | Author: {a['author_name'] or 'System'}")
            print("-" * 50)
            
        view_choice = input("Enter Article ID to read full text (or press Enter to return): ").strip()
        if view_choice:
            try:
                read_article(int(view_choice))
            except ValueError:
                print("Invalid article ID.")
    except Exception as e:
        print(f"Error loading article library: {e}")

def read_article(article_id):
    """View full content of a selected article."""
    try:
        art = execute_mysql_query(
            """
            SELECT a.title, a.body, a.topic, a.created_at, u.full_name AS author_name
            FROM articles a
            LEFT JOIN users u ON a.author_id = u.user_id
            WHERE a.article_id = %s
            """,
            (article_id,),
            fetchone=True
        )
        if not art:
            print("Error: Article not found.")
            return
            
        date_str = art["created_at"].strftime("%Y-%m-%d") if hasattr(art["created_at"], "strftime") else str(art["created_at"])
        print("\n" + "="*60)
        print(f"TOPIC: {art['topic'].upper()}")
        print(art["title"].upper())
        print(f"By {art['author_name'] or 'System'} on {date_str}")
        print("="*60)
        print(art["body"])
        print("="*60 + "\n")
        input("Press Enter to continue...")
    except Exception as e:
        print(f"Error loading full article: {e}")

def search_articles():
    """Search articles using MySQL FULLTEXT search."""
    print("\n--- Search Articles ---")
    query = input("Enter search keywords: ").strip()
    if not query:
        print("Search query cannot be empty.")
        return
        
    try:
        # Perform MySQL MATCH AGAINST parameterized query (No f-strings)
        articles = execute_mysql_query(
            """
            SELECT a.article_id, a.title, a.topic, a.created_at, u.full_name AS author_name,
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
            # Fallback to simple LIKE search if FULLTEXT scores yield 0 (common for small seed tables)
            like_query = f"%{query}%"
            articles = execute_mysql_query(
                """
                SELECT a.article_id, a.title, a.topic, a.created_at, u.full_name AS author_name
                FROM articles a
                LEFT JOIN users u ON a.author_id = u.user_id
                WHERE a.title LIKE %s OR a.body LIKE %s OR a.topic LIKE %s
                ORDER BY a.created_at DESC
                """,
                (like_query, like_query, like_query),
                fetchall=True
            )
            
        if not articles:
            print(f"No articles matched your search keywords: '{query}'")
            return
            
        print(f"\nFound {len(articles)} Match(es) for '{query}':")
        for a in articles:
            date_str = a["created_at"].strftime("%Y-%m-%d") if hasattr(a["created_at"], "strftime") else str(a["created_at"])
            print(f"ID: {a['article_id']} | [{a['topic'].upper()}] - {a['title']}")
            print(f"  Published: {date_str} | Author: {a['author_name'] or 'System'}")
            print("-" * 50)
            
        view_choice = input("Enter Article ID to read full text (or press Enter to return): ").strip()
        if view_choice:
            try:
                read_article(int(view_choice))
            except ValueError:
                print("Invalid article ID.")
    except Exception as e:
        print(f"Error querying articles: {e}")

def publish_article_admin(session):
    """Admin publishes a new article."""
    print("\n--- Publish New Article (Admin Console) ---")
    title = input("Enter Article Title: ").strip()
    if not title:
        print("Error: Title cannot be empty.")
        return
        
    topic = input("Enter Topic/Category (e.g., Self-Care, Anxiety, Coping): ").strip()
    if not topic:
        print("Error: Topic cannot be empty.")
        return
        
    print("Enter Article Body (press Ctrl+Z or Ctrl+D on empty line to finish typing, or type all in one line):")
    # Multi-line input gather
    body_lines = []
    try:
        while True:
            line = input()
            body_lines.append(line)
    except EOFError:
        pass
        
    body = "\n".join(body_lines).strip()
    if not body:
        # Fallback to single line if multi-line is skipped
        body = input("Or type single line body: ").strip()
        if not body:
            print("Error: Body cannot be empty.")
            return
            
    try:
        execute_mysql_query(
            "INSERT INTO articles (title, body, topic, author_id) VALUES (%s, %s, %s, %s)",
            (title, body, topic, session["user_id"]),
            commit=True
        )
        print("\nSuccess: New educational resource published successfully!")
    except Exception as e:
        print(f"Error publishing article: {e}")

def delete_article_admin():
    """Admin deletes an article."""
    print("\n--- Delete Article ---")
    art_id_str = input("Enter Article ID to delete: ").strip()
    try:
        art_id = int(art_id_str)
    except ValueError:
        print("Error: Invalid ID format.")
        return
        
    try:
        # Check if exists
        exists = execute_mysql_query("SELECT title FROM articles WHERE article_id = %s", (art_id,), fetchone=True)
        if not exists:
            print("Error: Article does not exist.")
            return
            
        confirm = input(f"Are you sure you want to permanently delete '{exists['title']}'? (y/n): ").strip().lower()
        if confirm == "y":
            execute_mysql_query("DELETE FROM articles WHERE article_id = %s", (art_id,), commit=True)
            print("Success: Article successfully removed.")
        else:
            print("Deletion cancelled.")
    except Exception as e:
        print(f"Error deleting article: {e}")
