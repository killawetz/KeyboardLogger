from queue import Queue
from pynput import keyboard
from datetime import datetime, timezone


class KeyListener:
    def __init__(self, events_buffer: Queue):
        self._events_buffer = events_buffer
        self._pressed_vks = set()

    def get_vk(self, key):
        """Retrieves a stable virtual-key code regardless of the object type and modifiers"""
        if isinstance(key, keyboard.KeyCode):
            return key.vk
        if isinstance(key, keyboard.Key):
            return key.value.vk
        return None

    def canonical_key_name(self, key) -> str:
        vk = self.get_vk(key)
        if vk is not None:
            return f"vk_{vk}"
        return str(key)

    def on_press(self, key):
        key_name = self.canonical_key_name(key)
        if key_name in self._pressed_vks:
            return
        self._pressed_vks.add(key_name)
        self._events_buffer.put((
            key_name,
            datetime.now(tz=timezone.utc).timestamp(),  # (3) float вместо объекта
            "press"
        ))

    def on_release(self, key):
        key_name = self.canonical_key_name(key)
        self._pressed_vks.discard(key_name)
        self._events_buffer.put((
            key_name,
            datetime.now(tz=timezone.utc).timestamp(),  # (3)
            "release"
        ))