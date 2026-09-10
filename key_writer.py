import logging
import queue
import threading
import time
import sqlite3
from queue import Queue

logger = logging.getLogger(__name__)


class KeyWriter:
    _BATCH_SIZE = 100
    _FLUSH_INTERVAL = 30  # seconds

    def __init__(self, events_buffer: Queue, db_path: str, session_id: int):
        self._events_buffer = events_buffer
        self._db_path = db_path
        self._session_id = session_id
        self._stop_event = threading.Event()
        self._flushing_thread = threading.Thread(
            target=self._flush_loop,
            daemon=False,
            name="flushing-thread"
        )

    def _flush_loop(self):
        try:
            conn = sqlite3.connect(self._db_path)
            logger.info("Flushing thread started")
            pack = []
            last_flush = time.monotonic()

            try:
                while not self._stop_event.is_set():
                    try:
                        event = self._events_buffer.get(timeout=1)
                        pack.append(event + (self._session_id,))
                    except queue.Empty:
                        pass

                    elapsed = time.monotonic() - last_flush
                    if len(pack) >= self._BATCH_SIZE or (pack and elapsed >= self._FLUSH_INTERVAL):
                        self._flush(conn, pack)
                        pack.clear()
                        last_flush = time.monotonic()

                while True:
                    try:
                        event = self._events_buffer.get_nowait()
                        pack.append(event + (self._session_id,))
                    except queue.Empty:
                        break

            finally:
                if pack:
                    self._flush(conn, pack)
                conn.close()

        except Exception:
            logger.exception("Unhandled exception in flush loop")
            raise

    def _flush(self, conn: sqlite3.Connection, pack: list):
        conn.executemany(
            """
            INSERT INTO key_events (key_name, event_time, event_type, session_id)
            VALUES (?, ?, ?, ?)
            """,
            pack
        )
        conn.commit()
        logger.debug("Flushed %s events to DB", len(pack))  # debug

    def start(self):
        self._flushing_thread.start()

    def stop(self):
        self._stop_event.set()
        self._flushing_thread.join(timeout=10)