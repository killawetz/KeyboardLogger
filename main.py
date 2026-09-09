from pynput import keyboard

import connection
from key_logger import KeyLogger


def main():
    conn = connection.get_connection("app.db")
    session_id = connection.get_session()

    key_logger = KeyLogger(conn, session_id)

    listener = keyboard.Listener(
        on_press=key_logger.on_press,
        on_release=key_logger.on_release
    )

    listener.start()
    listener.join()

