import numpy as np
import pywinctl
import mss
import os
import json
import threading
import asyncio
import time
from pynput import keyboard, mouse


ACTION_DETECTION_HISTORY_DIR = "neuro_core/data/action_detection"
os.makedirs(ACTION_DETECTION_HISTORY_DIR, exist_ok=True)


class ActionDetection:
    def __init__(self, user_name: str):
        self.user_name = user_name
        self.thread = None
        self._stop_event = threading.Event()

        self.user_history_dir_path = os.path.join(
            ACTION_DETECTION_HISTORY_DIR, user_name
        )
        os.makedirs(self.user_history_dir_path, exist_ok=True)

        self.actions = []

        keyboard_listener = keyboard.Listener(on_press=self.on_key_press)
        keyboard_listener.start()

        mouse_listener = mouse.Listener(
            on_click=self.on_click, on_scroll=self.on_scroll
        )
        mouse_listener.start()

    def on_click(self, x, y, button, pressed):
        """Handle mouse click events."""
        if not pressed:
            action = {
                "type": "mouse_click",
                "button": str(button),
                "position": (x, y),
                "timestamp": time.time(),
            }
            self.actions.append(action)

    def on_scroll(self, x, y, dx, dy):
        """Handle mouse scroll events."""
        action = {
            "type": "mouse_scroll",
            "direction": "down" if dy < 0 else "up",
            "position": (x, y),
            "timestamp": time.time(),
        }
        self.actions.append(action)

    def on_key_press(self, key):
        """Handle keyboard key press events."""
        try:
            action = {
                "type": "key_press",
                "keys": [str(key).strip("'")],
                "timestamp": time.time(),
            }
            self.actions.append(action)

        except AttributeError:
            action = {
                "type": "special_key_press",
                "key": str(key),
                "timestamp": time.time(),
            }
            self.actions.append(action)

    async def read_actions(self):
        """Read actions from the action queue and process them."""

        last_key_press_action = {}
        while not self._stop_event.is_set():
            if self.actions:
                print(last_key_press_action)
                print(self.actions)
                action = self.actions.pop(0)

                win_data = await self.get_active_window_info()
                if not win_data:
                    continue

                action.update(win_data)

                active_window_img = await self.get_active_window_img(win_data)

                # TODO: далі витяг елементів інтерфейсу та тексту на елементах, співвідношення координат кліків/текст вводу та елементів інтерфейсу

                app_name = action["app_name"]
                print(action["type"])
                if action["type"] == "key_press":
                    printing = True
                    last_app_action = last_key_press_action.get(app_name, {})
                    if last_app_action:
                        keys = last_app_action.get("keys", [])
                        keys.append(action["keys"][0])
                        last_app_action.update(action)
                        last_app_action["keys"] = keys
                        last_key_press_action[app_name] = last_app_action
                    else:
                        last_key_press_action[app_name] = action
                else:
                    printing = False

                if not printing and last_key_press_action.get(app_name):
                    print("hi")
                    await self.save_action_to_history(
                        last_key_press_action[app_name], app_name
                    )
                    del last_key_press_action[app_name]

                if not printing:
                    await self.save_action_to_history(action, action["app_name"])
            else:
                await asyncio.sleep(0.01)

    @staticmethod
    async def get_active_window_info() -> dict | None:
        """Get information about the active window."""
        loop = asyncio.get_running_loop()

        win = await loop.run_in_executor(None, pywinctl.getActiveWindow)
        if win and win.isVisible and win.isActive and win.title and win.getAppName():
            return {
                "win_name": win.title,
                "bbox": (win.left, win.top, win.right, win.bottom),
                "app_name": win.getAppName(),
                "pid": win.getPID(),
            }
        return None

    @staticmethod
    async def get_active_window_img(win_data: dict) -> np.ndarray:
        """Get image of the active window."""

        left, top, right, bottom = win_data["bbox"]
        width = right - left
        height = bottom - top

        loop = asyncio.get_running_loop()

        with mss.mss() as sct:

            image = await loop.run_in_executor(
                None,
                lambda: sct.grab(
                    {"left": left, "top": top, "width": width, "height": height}
                ),
            )

            img_np = np.array(image)[:, :, :3]
            return img_np

    async def save_action_to_history(self, action: dict, app_name: str):
        """Save action to the user's history file."""

        app_history_file_path = os.path.join(
            self.user_history_dir_path, f"{app_name}.json"
        )

        if os.path.exists(app_history_file_path):
            with open(app_history_file_path, "r") as file:
                history = json.load(file)

            with open(app_history_file_path, "w") as file:
                history.append(action)
                json.dump(history, file, indent=4, ensure_ascii=False)
        else:
            with open(app_history_file_path, "w") as file:
                json.dump([action], file, indent=4, ensure_ascii=False)

    def stop(self):
        """Stop the action detection."""
        self._stop_event.set()
        if self.thread:
            self.thread.join()

    def start(self):
        """Start the action detection."""
        if self.thread and self.thread.is_alive():
            return
        self._stop_event.clear()
        self.thread = threading.Thread(
            target=self._run_async_loop_in_thread, daemon=True
        )
        self.thread.start()

    def _run_async_loop_in_thread(self):
        asyncio.run(self.read_actions())
