import socket
from queue import Queue
from datetime import datetime, timezone

from pynput import keyboard

import connection
from key_listener import KeyListener
from key_writer import KeyWriter


def start_session(db_path: str):
    conn = connection.get_connection(db_path)

    started_at = datetime.timestamp(datetime.now(tz=timezone.utc))
    hostname = socket.gethostname()
    cursor = conn.execute(
        """
        INSERT INTO sessions (started_at, hostname)
        VALUES (?, ?)
        """,
    (started_at, hostname)
    )
    session_id = cursor.lastrowid
    conn.commit()
    conn.close()

    key_buffer = Queue()
    key_logger = KeyListener(key_buffer)
    key_writer = KeyWriter(key_buffer, db_path, session_id)

    listener = keyboard.Listener(
        on_press=key_logger.on_press,
        on_release=key_logger.on_release
    )

    key_writer.start()
    listener.start()
    try:
        listener.join()
    except KeyboardInterrupt:
        pass
    finally:
        listener.stop()
        key_writer.stop()
        conn = connection.get_connection(db_path)
        ended_at = datetime.timestamp(datetime.now(tz=timezone.utc))
        conn.execute(
            """
            UPDATE sessions
            SET ended_at = ?
            WHERE id = ?
            """,
            (ended_at, session_id)
        )
        conn.commit()
        conn.close()




def main():
    db_path = "app.db"
    start_session(db_path)
