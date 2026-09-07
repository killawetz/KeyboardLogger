from pynput import keyboard


pressed_vks = set()

def get_vk(key):
    """Retrieves a stable virtual-key code regardless of the object type and modifiers"""
    if isinstance(key, keyboard.KeyCode):
        return key.vk
    if isinstance(key, keyboard.Key):
        return key.value.vk
    return None

def on_press(key):
    vk = get_vk(key)

    print(f"[PRESS] {vk}")

def on_release(key):
    vk = get_vk(key)

    print(f"[RELEASE] {vk}")


listener = keyboard.Listener(
    on_press=on_press,
    on_release=on_release
)

listener.start()

while True:
    pass
