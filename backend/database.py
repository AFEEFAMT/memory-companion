import sqlite3
import os
from datetime import datetime, date

DATABASE_PATH = os.path.join(os.path.dirname(__file__), 'memory_companion.db')

def get_db_connection():
    conn = sqlite3.connect(DATABASE_PATH)
    conn.row_factory = sqlite3.Row
    return conn

def init_database():
    conn = get_db_connection()
    with open('schema.sql', 'r') as f:
        conn.executescript(f.read())
    
    cursor = conn.cursor()
    cursor.execute("SELECT COUNT(*) FROM patients")
    if cursor.fetchone()[0] == 0:
        cursor.execute("INSERT INTO patients (name) VALUES (?)", ("John",))
        
        today = date.today().isoformat()
        default_tasks = [
            ("morning_medicine", "09:00", today),
            ("breakfast", "09:30", today),
            ("lunch", "13:00", today),
            ("evening_walk", "17:00", today),
            ("dinner", "19:00", today),
            ("night_medicine", "21:00", today)
        ]
        cursor.executemany(
            "INSERT INTO tasks (patient_id, task_name, scheduled_time, date) VALUES (1, ?, ?, ?)",
            default_tasks
        )
    
    conn.commit()
    conn.close()

def get_patient_id():
    conn = get_db_connection()
    patient = conn.execute("SELECT id FROM patients LIMIT 1").fetchone()
    conn.close()
    return patient['id'] if patient else None
def create_task(patient_id, task_name, scheduled_time):
    conn = get_db_connection()
    today = date.today().isoformat()
    
    existing = conn.execute(
        "SELECT id FROM tasks WHERE patient_id = ? AND task_name = ? AND date = ?",
        (patient_id, task_name, today)
    ).fetchone()
    
    if not existing:
        conn.execute(
            "INSERT INTO tasks (patient_id, task_name, scheduled_time, date, completed) VALUES (?, ?, ?, ?, 0)",
            (patient_id, task_name, scheduled_time, today)
        )
        conn.commit()
        conn.close()
        return True
    
    conn.close()
    return False

def get_all_tasks(patient_id):
    conn = get_db_connection()
    today = date.today().isoformat()
    tasks = conn.execute(
        "SELECT * FROM tasks WHERE patient_id = ? AND date = ? ORDER BY scheduled_time",
        (patient_id, today)
    ).fetchall()
    conn.close()
    return [dict(task) for task in tasks]

def mark_task_completed(patient_id, task_name):
    conn = get_db_connection()
    today = date.today().isoformat()
    conn.execute(
        "UPDATE tasks SET completed = 1, completed_at = ? WHERE patient_id = ? AND task_name = ? AND date = ?",
        (datetime.now().isoformat(), patient_id, task_name, today)
    )
    conn.commit()
    conn.close()

def add_memory_note(patient_id, note_text, reminder_time=None):
    conn = get_db_connection()
    conn.execute(
        "INSERT INTO memory_notes (patient_id, note_text, reminder_time) VALUES (?, ?, ?)",
        (patient_id, note_text, reminder_time)
    )
    conn.commit()
    conn.close()

def get_memory_notes(patient_id):
    conn = get_db_connection()
    notes = conn.execute(
        "SELECT * FROM memory_notes WHERE patient_id = ? ORDER BY created_at DESC LIMIT 10",
        (patient_id,)
    ).fetchall()
    conn.close()
    return [dict(note) for note in notes]

def save_conversation(patient_id, user_message, agent_response):
    conn = get_db_connection()
    conn.execute(
        "INSERT INTO conversation_history (patient_id, user_message, agent_response) VALUES (?, ?, ?)",
        (patient_id, user_message, agent_response)
    )
    conn.commit()
    conn.close()

def get_recent_conversations(patient_id, limit=5):
    conn = get_db_connection()
    conversations = conn.execute(
        "SELECT * FROM conversation_history WHERE patient_id = ? ORDER BY timestamp DESC LIMIT ?",
        (patient_id, limit)
    ).fetchall()
    conn.close()
    return [dict(conv) for conv in reversed(conversations)]

def record_contact_call(patient_id, caller_name):
    conn = get_db_connection()
    conn.execute(
        "INSERT INTO contact_calls (patient_id, caller_name) VALUES (?, ?)",
        (patient_id, caller_name)
    )
    conn.commit()
    conn.close()

def get_recent_caller(patient_id):
    conn = get_db_connection()
    call = conn.execute(
        "SELECT caller_name, call_time FROM contact_calls WHERE patient_id = ? ORDER BY call_time DESC LIMIT 1",
        (patient_id,)
    ).fetchone()
    conn.close()
    return dict(call) if call else None

def update_task_status(task_id, is_completed):
    conn = get_db_connection()
    
    completed_int = 1 if is_completed else 0
    completed_at = datetime.now().isoformat() if is_completed else None
    
    conn.execute(
        "UPDATE tasks SET completed = ?, completed_at = ? WHERE id = ?",
        (completed_int, completed_at, task_id)
    )
    conn.commit()
    conn.close()

def delete_all_memory_notes(patient_id):
    conn = get_db_connection()
    conn.execute("DELETE FROM memory_notes WHERE patient_id = ?", (patient_id,))
    conn.commit()
    conn.close()

def delete_task(patient_id, task_name):
    """Deletes a specific task by name (fuzzy match handled in engine, exact here)"""
    conn = get_db_connection()
    today = date.today().isoformat()
    
    # We delete based on name and date (today)
    conn.execute(
        "DELETE FROM tasks WHERE patient_id = ? AND task_name = ? AND date = ?",
        (patient_id, task_name, today)
    )
    changes = conn.total_changes
    conn.commit()
    conn.close()
    return changes > 0

def delete_all_tasks(patient_id):
    """Clears all tasks for today"""
    conn = get_db_connection()
    today = date.today().isoformat()
    conn.execute(
        "DELETE FROM tasks WHERE patient_id = ? AND date = ?",
        (patient_id, today)
    )
    conn.commit()
    conn.close()