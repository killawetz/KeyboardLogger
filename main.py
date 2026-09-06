from pynput import keyboard

def on_press(key):
    try:
        print(f"Key {key} pressed.")
    except AttributeError:
        print('special key {} pressed'.format(
            key))


listener = keyboard.Listener(
    on_press=on_press)
listener.start()