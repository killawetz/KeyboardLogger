import sqlite3
import threading
from collections import deque
from queue import Queue
from pynput import keyboard
from datetime import datetime, timezone

class KeyLogger:
    def __init__(self, conn: sqlite3.Connection, session_id: int):
        self._conn = conn
        self._session_id = session_id
        self._events_buffer = Queue(maxsize=255)
        self._pressed_vks = set()
        self.flushing_thread = threading.Thread(target=self.flush_buffer, daemon=True)

        self.flushing_thread.start()
        self.flushing_thread.join()


    def get_vk(self, key):
        """Retrieves a stable virtual-key code regardless of the object type and modifiers"""
        if isinstance(key, keyboard.KeyCode):
            return key.vk
        if isinstance(key, keyboard.Key):
            return key.value.vk
        return None

    def on_press(self, key):
        key_name = self.canonical_key_name(key)

        if key_name in self._pressed_vks:
            return
        self._pressed_vks.add(key_name)

        self._events_buffer.put((key_name, datetime.now(tz=timezone.utc), "press"))

        print(f"[PRESS] {key_name}")

    def on_release(self, key):
        key_name = self.canonical_key_name(key)

        if key_name in self._pressed_vks:
            self._pressed_vks.discard(key_name)

        self._events_buffer.put((key_name, datetime.now(tz=timezone.utc), "release"))
        print(f"[RELEASE] {key_name}")

    def flush_buffer(self):
        pack = deque()

        while True:
            event: tuple[str, datetime, str] = self._events_buffer.get(timeout=None)
            pack.append(event + (self._session_id, ))
            if len(pack) >= 255:
                self._conn.executemany(
                    """
                    INSERT INTO key_events (key_name, event_time, event_type, session)
                    VALUES (?, ?, ?, ?)
                    """,
                    pack
                )
                self._conn.commit()
                pack.clear()

    def canonical_key_name(self, key) -> str:
        vk = self.get_vk(key)
        if vk is not None:
            return f"vk_{vk}"
        return str(key)