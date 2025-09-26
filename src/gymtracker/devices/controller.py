from __future__ import annotations

from typing import Callable

from evdev import InputDevice, categorize, ecodes
import threading

class Controller:
    def __init__(self, event_device_path="/dev/input/event5"):
        self.event_device_path = event_device_path
        self.is_running = True
        self._listener_lock = threading.Lock()
        self._listener: Callable[[str], None] | None = None
        self.controller_thread = threading.Thread(target=self._monitor_controller, daemon=True)
        self.controller_thread.start()

    def _monitor_controller(self):
        try:
            gamepad = InputDevice(self.event_device_path)
            for event in gamepad.read_loop():
                if not self.is_running:  # Check if we need to stop
                    break  # Exit loop when stopping
                # Handle button events (e.g., Button A, Button B)
                if event.type == ecodes.EV_KEY:
                    key_event = categorize(event)
                    if key_event.keystate == 1 and key_event.keycode:  # Button pressed
                        # Notify listeners for valid keycode events
                        self._notify_listener(key_event.keycode[0])

                # Handle D-pad axis events (e.g., arrow keys)
                elif event.type == ecodes.EV_ABS:
                    # Handle horizontal D-pad movement (left/right)
                    if event.code == ecodes.ABS_HAT0X:
                        if event.value == 1:
                            self._notify_listener("RIGHT")
                        elif event.value == -1:
                            self._notify_listener("LEFT")

                    # Handle vertical D-pad movement (up/down)
                    elif event.code == ecodes.ABS_HAT0Y:
                        if event.value == 1:
                            self._notify_listener("DOWN")
                        elif event.value == -1:
                            self._notify_listener("UP")
        except Exception as e:
            self.is_running = False

    def _notify_listener(self, keycode: str) -> None:
        callback: Callable[[str], None] | None
        with self._listener_lock:
            callback = self._listener
        if callback is not None:
            callback(keycode)

    def set_listener(self, callback: Callable[[str], None] | None) -> None:
        with self._listener_lock:
            self._listener = callback

    def stop(self):
        """Stop the controller monitoring thread."""
        self.is_running = False
