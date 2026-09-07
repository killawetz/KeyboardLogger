import sqlite3


from pynput import keyboard
from collections import deque
from datetime import datetime
from datetime import timezone

import connection

pressed_vks = set()
key_buffer = deque()
conn: sqlite3.Connection
session_id: int


def main():
    global conn
    conn = connection.get_connection("app.db")

    global session_id
    session_id = connection.get_session()

    listener = keyboard.Listener(
        on_press=on_press,
        on_release=on_release
    )

    listener.start()
    listener.join()

