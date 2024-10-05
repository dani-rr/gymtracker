from evdev import InputDevice, categorize, ecodes
import threading

class Controller:
    def __init__(self, event_device_path="/dev/input/event4"):
        self.event_device_path = event_device_path
        self.listeners = []
        self.is_running = True
        self.controller_thread = threading.Thread(target=self._monitor_controller, daemon=True)
        self.controller_thread.start()

    def _monitor_controller(self):
        try:
            gamepad = InputDevice(self.event_device_path)
            
            for event in gamepad.read_loop():
                # Handle button events (e.g., Button A, Button B)
                if event.type == ecodes.EV_KEY:
                    key_event = categorize(event)
                    if key_event.keystate == 1 and key_event.keycode:  # Button pressed
                        # Notify listeners for valid keycode events
                        self._notify_listeners(key_event.keycode[0])

                # Handle D-pad axis events (e.g., arrow keys)
                elif event.type == ecodes.EV_ABS:
                    # Handle horizontal D-pad movement (left/right)
                    if event.code == ecodes.ABS_HAT0X:
                        if event.value == 1:
                            self._notify_listeners("RIGHT")
                        elif event.value == -1:
                            self._notify_listeners("LEFT")

                    # Handle vertical D-pad movement (up/down)
                    elif event.code == ecodes.ABS_HAT0Y:
                        if event.value == 1:
                            self._notify_listeners("DOWN")
                        elif event.value == -1:
                            self._notify_listeners("UP")
        except Exception as e:
            print(f"Error with controller: {e}")
            self.is_running = False

    def _notify_listeners(self, keycode):
        # Notify all registered listeners with the keycode
        for callback in self.listeners:
            callback(keycode)

    def register_listener(self, callback):
        """
        Register a function that will be called when a button is pressed.
        The callback should accept one argument: the keycode of the pressed button.
        """
        self.listeners.append(callback)

    def stop(self):
        """Stop the controller monitoring thread."""
        self.is_running = False
