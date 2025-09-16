from models.db import get_connection
import bcrypt

# --------------------
# USUARIOS
# --------------------
def create_user(username, email, password):
    hashed = bcrypt.hashpw(password.encode('utf-8'), bcrypt.gensalt())
    conn = get_connection()
    cur = conn.cursor()
    cur.execute("INSERT INTO users (username, email, password) VALUES (%s, %s, %s)",
                (username, email, hashed))
    conn.commit()
    cur.close()
    conn.close()

def get_user_by_email(email):
    conn = get_connection()
    cur = conn.cursor(dictionary=True)
    cur.execute("SELECT * FROM users WHERE email=%s", (email,))
    user = cur.fetchone()
    cur.close()
    conn.close()
    return user

# --------------------
# CHATS
# --------------------
def save_chat(user_id, message):
    conn = get_connection()
    cur = conn.cursor()
    cur.execute("INSERT INTO chats (user_id, message) VALUES (%s, %s)", (user_id, message))
    conn.commit()
    cur.close()
    conn.close()

def get_user_chats(user_id):
    conn = get_connection()
    cur = conn.cursor(dictionary=True)
    cur.execute("SELECT * FROM chats WHERE user_id=%s ORDER BY created_at DESC", (user_id,))
    chats = cur.fetchall()
    cur.close()
    conn.close()
    return chats