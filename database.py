import sqlite3
from datetime import datetime

import pandas as pd

from config import DB_PATH


def get_connection():
    connection = sqlite3.connect(str(DB_PATH), timeout=10)
    connection.execute("PRAGMA foreign_keys = ON")
    return connection


def create_tables():
    conn = get_connection()
    try:
        cursor = conn.cursor()

        cursor.execute("""
            CREATE TABLE IF NOT EXISTS users (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                name TEXT NOT NULL,
                email TEXT NOT NULL,
                employee_id TEXT NOT NULL UNIQUE,
                face_encoding BLOB NOT NULL,
                created_at TEXT NOT NULL
            )
        """)

        cursor.execute("""
            CREATE TABLE IF NOT EXISTS attendance (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                user_id INTEGER NOT NULL,
                login_time TEXT NOT NULL,
                logout_time TEXT,
                FOREIGN KEY (user_id)
                    REFERENCES users(id)
                    ON DELETE CASCADE
            )
        """)

        conn.commit()
    finally:
        conn.close()


def register_user(name, email, employee_id, face_encoding):
    if face_encoding is None:
        raise ValueError("Face encoding is required.")

    try:
        encoding_bytes = face_encoding.tobytes()
    except AttributeError as exc:
        raise ValueError("Invalid face encoding.") from exc

    created_at = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

    conn = get_connection()
    try:
        cursor = conn.cursor()
        cursor.execute(
            """
            INSERT INTO users
            (name, email, employee_id, face_encoding, created_at)
            VALUES (?, ?, ?, ?, ?)
            """,
            (
                name,
                email,
                employee_id,
                encoding_bytes,
                created_at,
            ),
        )
        conn.commit()
        return cursor.lastrowid
    except sqlite3.IntegrityError as exc:
        if "employee_id" in str(exc).lower():
            raise ValueError("Employee ID already exists.") from exc
        raise ValueError(f"Database error: {exc}") from exc
    finally:
        conn.close()


def get_users():
    conn = get_connection()
    try:
        cursor = conn.cursor()
        cursor.execute(
            """
            SELECT id, name, email, employee_id, face_encoding
            FROM users
            ORDER BY id
            """
        )
        return cursor.fetchall()
    finally:
        conn.close()


def get_user_count():
    conn = get_connection()
    try:
        cursor = conn.cursor()
        cursor.execute("SELECT COUNT(*) FROM users")
        return cursor.fetchone()[0]
    finally:
        conn.close()


def has_active_login(user_id):
    conn = get_connection()
    try:
        cursor = conn.cursor()
        cursor.execute(
            """
            SELECT id
            FROM attendance
            WHERE user_id = ?
              AND logout_time IS NULL
            LIMIT 1
            """,
            (user_id,),
        )
        return cursor.fetchone() is not None
    finally:
        conn.close()


def save_login(user_id):
    if has_active_login(user_id):
        return False

    login_time = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

    conn = get_connection()
    try:
        cursor = conn.cursor()
        cursor.execute(
            """
            INSERT INTO attendance
            (user_id, login_time, logout_time)
            VALUES (?, ?, NULL)
            """,
            (user_id, login_time),
        )
        conn.commit()
        return cursor.rowcount == 1
    finally:
        conn.close()


def save_logout(user_id):
    logout_time = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

    conn = get_connection()
    try:
        cursor = conn.cursor()
        cursor.execute(
            """
            UPDATE attendance
            SET logout_time = ?
            WHERE id = (
                SELECT id
                FROM attendance
                WHERE user_id = ?
                  AND logout_time IS NULL
                ORDER BY id DESC
                LIMIT 1
            )
            """,
            (logout_time, user_id),
        )
        conn.commit()
        return cursor.rowcount == 1
    finally:
        conn.close()


def get_attendance():
    conn = get_connection()
    try:
        return pd.read_sql_query(
            """
            SELECT
                attendance.id AS Attendance_ID,
                users.name AS Name,
                users.email AS Email,
                users.employee_id AS Employee_ID,
                attendance.login_time AS Login_Time,
                attendance.logout_time AS Logout_Time
            FROM attendance
            INNER JOIN users
                ON attendance.user_id = users.id
            ORDER BY attendance.id DESC
            """,
            conn,
        )
    finally:
        conn.close()
