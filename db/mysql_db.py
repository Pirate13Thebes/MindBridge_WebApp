import os
import mysql.connector
from mysql.connector import Error
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

def get_mysql_conn():
    """Establish and return a raw MySQL connection."""
    return mysql.connector.connect(
        host=os.getenv("MYSQL_HOST", "localhost"),
        port=int(os.getenv("MYSQL_PORT", 3306)),
        user=os.getenv("MYSQL_USER", "root"),
        password=os.getenv("MYSQL_PASSWORD", ""),
        database=os.getenv("MYSQL_DATABASE", "mindbridge_db")
    )

def execute_mysql_query(query, params=None, fetchone=False, fetchall=False, commit=False):
    """
    Execute a parameterized SQL query safely.
    Handles connection lifecycle, committing writes, and closing cursors/connections in finally block.
    """
    conn = None
    cursor = None
    try:
        conn = get_mysql_conn()
        cursor = conn.cursor(dictionary=True)
        cursor.execute(query, params or ())
        
        result = None
        if fetchone:
            result = cursor.fetchone()
        elif fetchall:
            result = cursor.fetchall()
            
        if commit:
            conn.commit()
            
        return result
    except Error as e:
        print(f"MySQL Error: {e}")
        if conn and commit:
            try:
                conn.rollback()
            except Error:
                pass
        raise e
    finally:
        if cursor:
            cursor.close()
        if conn:
            conn.close()

def init_mysql_db():
    """Initialize MySQL Database: creates database if not exists and tables/indexes."""
    # First connect without database context to create database if missing
    conn = None
    cursor = None
    try:
        conn = mysql.connector.connect(
            host=os.getenv("MYSQL_HOST", "localhost"),
            port=int(os.getenv("MYSQL_PORT", 3306)),
            user=os.getenv("MYSQL_USER", "root"),
            password=os.getenv("MYSQL_PASSWORD", "")
        )
        cursor = conn.cursor()
        db_name = os.getenv("MYSQL_DATABASE", "mindbridge_db")
        cursor.execute(f"CREATE DATABASE IF NOT EXISTS {db_name}")
        conn.commit()
    except Error as e:
        print(f"Warning: Could not auto-create database '{os.getenv('MYSQL_DATABASE', 'mindbridge_db')}' due to: {e}")
    finally:
        if cursor:
            cursor.close()
        if conn:
            conn.close()

    # Now define tables
    queries = [
        """
        CREATE TABLE IF NOT EXISTS users (
            user_id INT AUTO_INCREMENT PRIMARY KEY,
            username VARCHAR(80) NOT NULL UNIQUE,
            password_hash VARCHAR(255) NOT NULL,
            role ENUM('patient','provider','admin','volunteer','family') NOT NULL,
            full_name VARCHAR(120) NOT NULL,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        ) ENGINE=InnoDB;
        """,
        """
        CREATE TABLE IF NOT EXISTS therapy_sessions (
            session_id INT AUTO_INCREMENT PRIMARY KEY,
            patient_id INT NOT NULL,
            therapist_id INT NOT NULL,
            session_date DATE NOT NULL,
            notes TEXT,
            status ENUM('scheduled','completed','cancelled') DEFAULT 'scheduled',
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (patient_id) REFERENCES users(user_id) ON DELETE CASCADE,
            FOREIGN KEY (therapist_id) REFERENCES users(user_id) ON DELETE CASCADE,
            INDEX idx_patient (patient_id),
            INDEX idx_date (session_date)
        ) ENGINE=InnoDB;
        """,
        """
        CREATE TABLE IF NOT EXISTS articles (
            article_id INT AUTO_INCREMENT PRIMARY KEY,
            title VARCHAR(200) NOT NULL,
            body LONGTEXT NOT NULL,
            topic VARCHAR(80),
            author_id INT,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (author_id) REFERENCES users(user_id) ON DELETE SET NULL,
            FULLTEXT INDEX ft_articles (title, body)
        ) ENGINE=InnoDB;
        """,
        """
        CREATE TABLE IF NOT EXISTS followup_records (
            record_id INT AUTO_INCREMENT PRIMARY KEY,
            patient_id INT NOT NULL,
            record_type ENUM('injection','medication','checkup') NOT NULL,
            description VARCHAR(255) NOT NULL,
            due_date DATE NOT NULL,
            status ENUM('pending','completed','overdue') DEFAULT 'pending',
            FOREIGN KEY (patient_id) REFERENCES users(user_id) ON DELETE CASCADE,
            INDEX idx_patient_due (patient_id, due_date)
        ) ENGINE=InnoDB;
        """
    ]
    
    # Execute table creation queries one by one
    for q in queries:
        execute_mysql_query(q, commit=True)
    
    print("MySQL database initialization completed successfully.")
