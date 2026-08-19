import os
import sqlite3
import threading
from contextlib import contextmanager
from datetime import datetime


class Memory:

    # ==========================================================
    # INITIALIZATION
    # ==========================================================

    def __init__(
        self,
        database="akhim_memory.db",
        max_message_length=20000
    ):

        self.database = os.path.abspath(
            database
        )

        self.max_message_length = (
            max_message_length
        )

        # ------------------------------------------------------
        # SQLite access lock
        # Important because AKHIM AI uses background threads.
        # ------------------------------------------------------

        self._lock = threading.RLock()

        self.create_table()

    # ==========================================================
    # DATABASE CONNECTION
    # ==========================================================

    @contextmanager
    def connect(self):

        conn = None

        try:

            conn = sqlite3.connect(
                self.database,
                timeout=10,
                check_same_thread=False
            )

            # --------------------------------------------------
            # Better SQLite behavior
            # --------------------------------------------------

            conn.execute(
                "PRAGMA foreign_keys = ON"
            )

            conn.execute(
                "PRAGMA busy_timeout = 10000"
            )

            yield conn

            conn.commit()

        except Exception:

            if conn is not None:

                try:
                    conn.rollback()
                except Exception:
                    pass

            raise

        finally:

            if conn is not None:

                try:
                    conn.close()
                except Exception:
                    pass

    # ==========================================================
    # CREATE TABLE
    # ==========================================================

    def create_table(self):

        with self._lock:

            with self.connect() as conn:

                cursor = conn.cursor()

                cursor.execute("""
                    CREATE TABLE IF NOT EXISTS messages (
                        id INTEGER PRIMARY KEY AUTOINCREMENT,
                        role TEXT NOT NULL,
                        message TEXT NOT NULL,
                        created_at TEXT NOT NULL
                    )
                """)

                # ------------------------------------------------
                # Index for fast recent-history lookup
                # ------------------------------------------------

                cursor.execute("""
                    CREATE INDEX IF NOT EXISTS
                    idx_messages_created
                    ON messages(id DESC)
                """)

    # ==========================================================
    # NORMALIZE ROLE
    # ==========================================================

    def normalize_role(self, role):

        role = str(
            role or ""
        ).strip().lower()

        allowed = {
            "user",
            "assistant",
            "system"
        }

        if role not in allowed:

            return "user"

        return role

    # ==========================================================
    # NORMALIZE MESSAGE
    # ==========================================================

    def normalize_message(self, message):

        if message is None:
            return ""

        message = str(
            message
        ).strip()

        if not message:
            return ""

        # ------------------------------------------------------
        # Prevent extremely large memory entries
        # ------------------------------------------------------

        if len(message) > self.max_message_length:

            message = message[
                :self.max_message_length
            ]

        return message

    # ==========================================================
    # SAVE MESSAGE
    # ==========================================================

    def save(
        self,
        role,
        message
    ):

        role = self.normalize_role(
            role
        )

        message = self.normalize_message(
            message
        )

        if not message:

            return False

        timestamp = datetime.utcnow().isoformat(
            timespec="seconds"
        )

        try:

            with self._lock:

                with self.connect() as conn:

                    cursor = conn.cursor()

                    cursor.execute(
                        """
                        INSERT INTO messages
                        (role, message, created_at)
                        VALUES (?, ?, ?)
                        """,
                        (
                            role,
                            message,
                            timestamp
                        )
                    )

            return True

        except sqlite3.Error:

            return False

    # ==========================================================
    # GET RECENT MESSAGES
    # ==========================================================

    def get_recent(
        self,
        limit=20
    ):

        try:

            limit = int(limit)

        except Exception:

            limit = 20

        # ------------------------------------------------------
        # Protect database from invalid/huge limits
        # ------------------------------------------------------

        limit = max(
            1,
            min(limit, 200)
        )

        try:

            with self._lock:

                with self.connect() as conn:

                    cursor = conn.cursor()

                    cursor.execute(
                        """
                        SELECT role, message
                        FROM messages
                        ORDER BY id DESC
                        LIMIT ?
                        """,
                        (limit,)
                    )

                    rows = cursor.fetchall()

            # --------------------------------------------------
            # Database returns newest first.
            # AI conversation should be oldest → newest.
            # --------------------------------------------------

            rows.reverse()

            return rows

        except sqlite3.Error:

            return []

    # ==========================================================
    # GET RECENT AS CONTEXT
    # ==========================================================

    def get_context(
        self,
        limit=20
    ):

        rows = self.get_recent(
            limit
        )

        if not rows:

            return ""

        parts = []

        for role, message in rows:

            if role == "user":

                parts.append(
                    "User: " + message
                )

            elif role == "assistant":

                parts.append(
                    "AKHIM AI: " + message
                )

            else:

                parts.append(
                    "System: " + message
                )

        return "\n".join(parts)

    # ==========================================================
    # GET MESSAGE COUNT
    # ==========================================================

    def count(self):

        try:

            with self._lock:

                with self.connect() as conn:

                    cursor = conn.cursor()

                    cursor.execute(
                        "SELECT COUNT(*) FROM messages"
                    )

                    row = cursor.fetchone()

                    return int(
                        row[0]
                    ) if row else 0

        except sqlite3.Error:

            return 0

    # ==========================================================
    # DELETE ALL MEMORY
    # ==========================================================

    def clear(self):

        try:

            with self._lock:

                with self.connect() as conn:

                    cursor = conn.cursor()

                    cursor.execute(
                        "DELETE FROM messages"
                    )

            return True

        except sqlite3.Error:

            return False

    # ==========================================================
    # DELETE LAST N MESSAGES
    # ==========================================================

    def delete_recent(
        self,
        count=1
    ):

        try:

            count = int(count)

        except Exception:

            count = 1

        count = max(
            1,
            min(count, 200)
        )

        try:

            with self._lock:

                with self.connect() as conn:

                    cursor = conn.cursor()

                    cursor.execute(
                        """
                        DELETE FROM messages
                        WHERE id IN (
                            SELECT id
                            FROM messages
                            ORDER BY id DESC
                            LIMIT ?
                        )
                        """,
                        (count,)
                    )

            return True

        except sqlite3.Error:

            return False

    # ==========================================================
    # GET LAST MESSAGE
    # ==========================================================

    def get_last(self):

        try:

            with self._lock:

                with self.connect() as conn:

                    cursor = conn.cursor()

                    cursor.execute(
                        """
                        SELECT role, message
                        FROM messages
                        ORDER BY id DESC
                        LIMIT 1
                        """
                    )

                    row = cursor.fetchone()

                    return row

        except sqlite3.Error:

            return None

    # ==========================================================
    # SEARCH MEMORY
    # ==========================================================

    def search(
        self,
        keyword,
        limit=20
    ):

        keyword = str(
            keyword or ""
        ).strip()

        if not keyword:

            return []

        try:

            limit = int(limit)

        except Exception:

            limit = 20

        limit = max(
            1,
            min(limit, 100)
        )

        try:

            with self._lock:

                with self.connect() as conn:

                    cursor = conn.cursor()

                    cursor.execute(
                        """
                        SELECT role, message
                        FROM messages
                        WHERE message LIKE ?
                        ORDER BY id DESC
                        LIMIT ?
                        """,
                        (
                            "%" + keyword + "%",
                            limit
                        )
                    )

                    rows = cursor.fetchall()

            rows.reverse()

            return rows

        except sqlite3.Error:

            return []

    # ==========================================================
    # DATABASE INFO
    # ==========================================================

    def info(self):

        return {
            "database": self.database,
            "messages": self.count()
        }