"""
ResuMatch AI — Database Layer
SQLite database for users, sessions, and activity logging.
"""

import os
import sqlite3
import time
from contextlib import contextmanager
from datetime import datetime

DB_PATH = os.path.join(os.path.dirname(__file__), "resumatch.db")


def get_db_path():
    return DB_PATH


@contextmanager
def get_db():
    """Context manager for database connections."""
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    conn.execute("PRAGMA journal_mode=WAL")
    conn.execute("PRAGMA foreign_keys=ON")
    try:
        yield conn
        conn.commit()
    except Exception:
        conn.rollback()
        raise
    finally:
        conn.close()


def init_db():
    """Initialize database tables and default admin account."""
    with get_db() as conn:
        conn.executescript("""
            CREATE TABLE IF NOT EXISTS users (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                email TEXT UNIQUE NOT NULL,
                name TEXT NOT NULL,
                password_hash TEXT NOT NULL,
                role TEXT NOT NULL DEFAULT 'user',
                created_at TEXT NOT NULL DEFAULT (datetime('now')),
                last_login TEXT,
                is_active INTEGER NOT NULL DEFAULT 1,
                is_verified INTEGER NOT NULL DEFAULT 0,
                verification_token TEXT
            );

            CREATE TABLE IF NOT EXISTS sessions (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                user_id INTEGER NOT NULL,
                login_at TEXT NOT NULL DEFAULT (datetime('now')),
                logout_at TEXT,
                ip_address TEXT,
                user_agent TEXT,
                FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE
            );

            CREATE TABLE IF NOT EXISTS activity_log (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                user_id INTEGER,
                action TEXT NOT NULL,
                details TEXT,
                timestamp TEXT NOT NULL DEFAULT (datetime('now')),
                FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE SET NULL
            );

            CREATE TABLE IF NOT EXISTS analyses (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                user_id INTEGER NOT NULL,
                filename TEXT,
                ats_score REAL,
                skills_count INTEGER,
                timestamp TEXT NOT NULL DEFAULT (datetime('now')),
                FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE
            );
        """)

        # Run database migrations dynamically for existing users table
        try:
            conn.execute("ALTER TABLE users ADD COLUMN is_verified INTEGER NOT NULL DEFAULT 1")
        except sqlite3.OperationalError:
            pass  # Column already exists

        try:
            conn.execute("ALTER TABLE users ADD COLUMN verification_token TEXT")
        except sqlite3.OperationalError:
            pass  # Column already exists

        # Create default admin if not exists
        existing = conn.execute("SELECT id FROM users WHERE email = ?", ("admin@resumatch.ai",)).fetchone()
        if not existing:
            import bcrypt
            pw_hash = bcrypt.hashpw("admin123".encode(), bcrypt.gensalt()).decode()
            conn.execute(
                "INSERT INTO users (email, name, password_hash, role, is_verified) VALUES (?, ?, ?, ?, ?)",
                ("admin@resumatch.ai", "Admin", pw_hash, "admin", 1)
            )
            print("[DB] Default admin created: admin@resumatch.ai / admin123")

    print("[DB] Database initialized [OK]")


# ──────── User operations ────────

def create_user(email: str, name: str, password_hash: str, verification_token: str = None, is_verified: int = 0) -> dict:
    with get_db() as conn:
        try:
            conn.execute(
                "INSERT INTO users (email, name, password_hash, verification_token, is_verified) VALUES (?, ?, ?, ?, ?)",
                (email, name, password_hash, verification_token, is_verified)
            )
            user = conn.execute("SELECT * FROM users WHERE email = ?", (email,)).fetchone()
            return dict(user)
        except sqlite3.IntegrityError:
            raise ValueError("Email already registered")


def verify_user_by_token(token: str) -> bool:
    """Mark user as verified and clear their token."""
    with get_db() as conn:
        cursor = conn.execute(
            "UPDATE users SET is_verified = 1, verification_token = NULL WHERE verification_token = ?",
            (token,)
        )
        return cursor.rowcount > 0


def get_user_by_verification_token(token: str) -> dict | None:
    """Retrieve user details by verification token."""
    with get_db() as conn:
        row = conn.execute("SELECT * FROM users WHERE verification_token = ?", (token,)).fetchone()
        return dict(row) if row else None


def get_user_by_email(email: str) -> dict | None:
    with get_db() as conn:
        row = conn.execute("SELECT * FROM users WHERE email = ?", (email,)).fetchone()
        return dict(row) if row else None


def get_user_by_id(user_id: int) -> dict | None:
    with get_db() as conn:
        row = conn.execute("SELECT * FROM users WHERE id = ?", (user_id,)).fetchone()
        return dict(row) if row else None


def update_last_login(user_id: int):
    with get_db() as conn:
        conn.execute(
            "UPDATE users SET last_login = datetime('now') WHERE id = ?", (user_id,)
        )


def get_all_users() -> list[dict]:
    with get_db() as conn:
        rows = conn.execute(
            "SELECT id, email, name, role, created_at, last_login, is_active FROM users ORDER BY created_at DESC"
        ).fetchall()
        return [dict(r) for r in rows]


def delete_user(user_id: int) -> bool:
    with get_db() as conn:
        result = conn.execute("DELETE FROM users WHERE id = ? AND role != 'admin'", (user_id,))
        return result.rowcount > 0


def update_user_role(user_id: int, new_role: str) -> bool:
    if new_role not in ("user", "admin"):
        return False
    with get_db() as conn:
        result = conn.execute("UPDATE users SET role = ? WHERE id = ?", (new_role, user_id))
        return result.rowcount > 0


# ──────── Session operations ────────

def create_session(user_id: int, ip: str = "", user_agent: str = "") -> int:
    with get_db() as conn:
        cursor = conn.execute(
            "INSERT INTO sessions (user_id, ip_address, user_agent) VALUES (?, ?, ?)",
            (user_id, ip, user_agent)
        )
        return cursor.lastrowid


def end_session(session_id: int):
    with get_db() as conn:
        conn.execute(
            "UPDATE sessions SET logout_at = datetime('now') WHERE id = ?", (session_id,)
        )


def get_recent_sessions(limit: int = 50) -> list[dict]:
    with get_db() as conn:
        rows = conn.execute("""
            SELECT s.id, s.login_at, s.logout_at, s.ip_address, s.user_agent,
                   u.email, u.name, u.role
            FROM sessions s
            JOIN users u ON s.user_id = u.id
            ORDER BY s.login_at DESC
            LIMIT ?
        """, (limit,)).fetchall()
        return [dict(r) for r in rows]


# ──────── Activity log ────────

def log_activity(user_id: int | None, action: str, details: str = ""):
    with get_db() as conn:
        conn.execute(
            "INSERT INTO activity_log (user_id, action, details) VALUES (?, ?, ?)",
            (user_id, action, details)
        )


def get_activity_log(limit: int = 100) -> list[dict]:
    with get_db() as conn:
        rows = conn.execute("""
            SELECT a.id, a.action, a.details, a.timestamp,
                   u.email, u.name
            FROM activity_log a
            LEFT JOIN users u ON a.user_id = u.id
            ORDER BY a.timestamp DESC
            LIMIT ?
        """, (limit,)).fetchall()
        return [dict(r) for r in rows]


# ──────── Analysis tracking ────────

def log_analysis(user_id: int, filename: str, ats_score: float, skills_count: int):
    with get_db() as conn:
        conn.execute(
            "INSERT INTO analyses (user_id, filename, ats_score, skills_count) VALUES (?, ?, ?, ?)",
            (user_id, filename, ats_score, skills_count)
        )


def get_stats() -> dict:
    with get_db() as conn:
        total_users = conn.execute("SELECT COUNT(*) FROM users").fetchone()[0]
        active_today = conn.execute(
            "SELECT COUNT(DISTINCT user_id) FROM sessions WHERE date(login_at) = date('now')"
        ).fetchone()[0]
        total_analyses = conn.execute("SELECT COUNT(*) FROM analyses").fetchone()[0]
        total_sessions = conn.execute("SELECT COUNT(*) FROM sessions").fetchone()[0]
        avg_ats = conn.execute("SELECT AVG(ats_score) FROM analyses").fetchone()[0]

        return {
            "total_users": total_users,
            "active_today": active_today,
            "total_analyses": total_analyses,
            "total_sessions": total_sessions,
            "avg_ats_score": round(avg_ats, 1) if avg_ats else 0,
        }
