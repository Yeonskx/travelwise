import os
import sqlite3
import hashlib

# --- Database setup ---
def get_db_path():
    """Get absolute database path and ensure folder exists."""
    db_dir = os.path.join(os.path.dirname(__file__), "..", "database")
    os.makedirs(db_dir, exist_ok=True)
    return os.path.join(db_dir, "users.db")

def init_db():
    """Create users table if it doesn’t exist."""
    conn = sqlite3.connect(get_db_path())
    c = conn.cursor()
    c.execute("""
        CREATE TABLE IF NOT EXISTS users (
            email TEXT PRIMARY KEY,
            password TEXT,
            firstname TEXT,
            lastname TEXT,
            country TEXT,
            role TEXT DEFAULT 'user'
        )
    """)
    conn.commit()
    conn.close()

# --- Password hashing ---
def hash_password(password):
    return hashlib.sha256(password.encode()).hexdigest()

# --- Add new user ---
def add_user(email, password, firstname, lastname, country, role='user'):
    conn = sqlite3.connect(get_db_path())
    c = conn.cursor()
    try:
        c.execute("""
            INSERT INTO users (email, password, firstname, lastname, country, role)
            VALUES (?, ?, ?, ?, ?, ?)
        """, (email, hash_password(password), firstname, lastname, country, role))
        conn.commit()
    except sqlite3.IntegrityError:
        # Prevents app crash if the email already exists
        print(f"User with email {email} already exists.")
    finally:
        conn.close()

# --- Validate login ---
def verify_user(email, password):
    conn = sqlite3.connect(get_db_path())
    c = conn.cursor()
    c.execute("""
        SELECT * FROM users WHERE email = ? AND password = ?
    """, (email, hash_password(password)))
    user = c.fetchone()
    conn.close()
    return user

# --- Check if email already exists ---
def email_exists(email):
    conn = sqlite3.connect(get_db_path())
    c = conn.cursor()
    c.execute("SELECT 1 FROM users WHERE email = ?", (email,))
    exists = c.fetchone()
    conn.close()
    return exists is not None
