import threading
import time
import random
from typing import Optional, Callable
import pyautogui
import keyboard
from datetime import datetime, time as dt_time

class AutoTyper:
    def __init__(self):
        """Initialize the AutoTyper with default settings."""
        self.running = False
        self.paused = False
        self.thread: Optional[threading.Thread] = None
        self.text = ""
        self.wpm = 60
        self.random_delay = {
            "enabled": False,
            "min": 100,  # 100 milliseconds
            "max": 1000  # 1000 milliseconds
        }
        self.interval = 0.0
        self.scheduled_time: Optional[dt_time] = None
        self.status_callback: Optional[Callable[[str], None]] = None
        self.progress_callback: Optional[Callable[[int, int], None]] = None
        
        # Set PyAutoGUI settings
        pyautogui.FAILSAFE = True
        pyautogui.PAUSE = 0.001

    def set_text(self, text: str) -> None:
        """Set the text to be typed."""
        self.text = text

    def set_wpm(self, wpm: int) -> None:
        """Set typing speed in words per minute."""
        self.wpm = max(1, min(wpm, 1000))  # Limit WPM between 1 and 1000

    def set_random_delay(self, enabled: bool, min_delay: float, max_delay: float) -> None:
        """
        Set random delay settings.
        min_delay and max_delay are in milliseconds
        """
        self.random_delay = {
            "enabled": enabled,
            "min": max(0.0, min_delay) / 1000.0,  # Convert to seconds
            "max": max(min_delay, max_delay) / 1000.0  # Convert to seconds
        }

    def set_interval(self, interval: float) -> None:
        """Set interval between typing sessions."""
        self.interval = max(0.0, interval)

    def set_scheduled_time(self, scheduled_time: Optional[dt_time]) -> None:
        """Set scheduled start time."""
        self.scheduled_time = scheduled_time

    def set_status_callback(self, callback: Callable[[str], None]) -> None:
        """Set callback for status updates."""
        self.status_callback = callback

    def set_progress_callback(self, callback: Callable[[int, int], None]) -> None:
        """Set callback for progress updates."""
        self.progress_callback = callback

    def update_status(self, status: str) -> None:
        """Update status through callback if set."""
        if self.status_callback:
            self.status_callback(status)

    def update_progress(self, current: int, total: int) -> None:
        """Update progress through callback if set."""
        if self.progress_callback:
            self.progress_callback(current, total)

    def calculate_delay(self) -> float:
        """Calculate delay between keystrokes based on WPM."""
        # Average word length is 5 characters
        cpm = self.wpm * 5
        return 60.0 / cpm

    def wait_for_scheduled_time(self) -> None:
        """Wait until scheduled time if set."""
        if self.scheduled_time:
            now = datetime.now().time()
            if now < self.scheduled_time:
                self.update_status("Waiting for scheduled time...")
                while datetime.now().time() < self.scheduled_time and self.running:
                    time.sleep(0.1)

    def type_text(self) -> None:
        """Main typing function."""
        try:
            # Wait 3 seconds before starting
            self.update_status("Starting in 3 seconds...")
            for i in range(3, 0, -1):
                if not self.running:
                    return
                self.update_status(f"Starting in {i} seconds...")
                time.sleep(1)

            while self.running:
                self.wait_for_scheduled_time()
                
                if not self.running:
                    break

                self.update_status("Typing in progress...")
                base_delay = self.calculate_delay()
                
                for i, char in enumerate(self.text):
                    while self.paused:
                        if not self.running:
                            return
                        time.sleep(0.1)
                    
                    if not self.running:
                        break

                    pyautogui.write(char)
                    
                    # Calculate and apply delay
                    if self.random_delay["enabled"]:
                        delay = random.uniform(
                            self.random_delay["min"],
                            self.random_delay["max"]
                        )
                    else:
                        delay = base_delay
                    
                    time.sleep(delay)
                    self.update_progress(i + 1, len(self.text))

                if self.interval <= 0:
                    break
                
                self.update_status(f"Waiting {self.interval} seconds before next iteration...")
                time.sleep(self.interval)

        except Exception as e:
            self.update_status(f"Error: {str(e)}")
        finally:
            self.running = False
            self.update_status("Stopped")

    def start(self) -> None:
        """Start the typing process in a new thread."""
        if not self.running and self.text:
            self.running = True
            self.paused = False
            self.thread = threading.Thread(target=self.type_text)
            self.thread.daemon = True
            self.thread.start()

    def stop(self) -> None:
        """Stop the typing process."""
        self.running = False
        self.paused = False
        if self.thread:
            self.thread.join(timeout=1.0)
        self.update_status("Stopped")

    def toggle_pause(self) -> None:
        """Toggle pause state."""
        if self.running:
            self.paused = not self.paused
            self.update_status("Paused" if self.paused else "Resumed")

    def is_running(self) -> bool:
        """Check if typing is in progress."""
        return self.running

    def is_paused(self) -> bool:
        """Check if typing is paused."""
        return self.paused
