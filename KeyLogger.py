import sqlite3
from queue import Queue

class KeyLogger:
    def __init__(self, conn: sqlite3.Connection, session_id: int, ):
        self._conn = conn
        self._session_id = session_id
        self._keys_buffer = Queue()
        self._pressed_vks = set()

    def get_vk(self, key):
        """Retrieves a stable virtual-key code regardless of the object type and modifiers"""
        if isinstance(key, keyboard.KeyCode):
            return key.vk
        if isinstance(key, keyboard.Key):
            return key.value.vk
        return None

    def on_press(self, key):
        key_name = canonical_key_name(key)

        if key_name in pressed_vks:
            return
        pressed_vks.add(key_name)

        key_buffer.appendleft((key_name, datetime.now(tz=timezone.utc), "press"))
        if len(key_buffer) > 255:
            flush_buffer()

        print(f"[PRESS] {key_name}")

    def on_release(self, key):
        key_name = canonical_key_name(key)

        if key_name in pressed_vks:
            pressed_vks.discard(key_name)

        key_buffer.appendleft((key_name, datetime.now(tz=datetime.UTC), "release"))
        print(f"[RELEASE] {key_name}")

    def flush_buffer(self):
        while key_buffer:
            key, timestamp, event_type = key_buffer.pop()
            conn.execute(
                """
                INSERT INTO key_events (key_name, event_time, event_type, session)
                VALUES (?, ?, ?, ?)
                """,
                (key, timestamp, event_type, session_id)
            )

    def canonical_key_name(self, key) -> str:
        vk = get_vk(key)
        if vk is not None:
            return f"vk_{vk}"
        return str(key)