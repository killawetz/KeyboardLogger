import socket
from queue import Queue
from datetime import datetime, timezone

from pynput import keyboard

import connection
from key_listener import KeyListener
from key_writer import KeyWriter


def start_session(db_path: str):
    conn = connection.get_connection(db_path)

    session_id: int = conn.execute(
        """
        SELECT COALESCE(MAX(id), 0) + 1
        FROM sessions;
        """
    ).fetchone()[0]
    started_at = datetime.timestamp(datetime.now(tz=timezone.utc))
    hostname = socket.gethostname()

    conn.execute(
        """
        INSERT INTO sessions (id, started_at, hostname) VALUES (?, ?, ?)
        """,
        (session_id, started_at, hostname)
    )
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
    listener.join()
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
