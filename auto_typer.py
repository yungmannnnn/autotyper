import threading
import time
import random
from typing import Optional, Callable
import keyboard
from datetime import datetime, time as dt_time
from contextlib import contextmanager
import queue
import itertools
import win32api
import win32con
import win32gui
import win32clipboard

class AutoTyper:
    def __init__(self):
        """Initialize the AutoTyper with optimized settings."""
        # Initialize all instance variables
        self.running = False
        self.paused = False
        self.thread = None
        self.text = ""
        self.wpm = 60
        self.random_delay = {
            "enabled": False,
            "min": 100,
            "max": 1000
        }
        self.interval = 0.0
        self.scheduled_time = None
        self._status_callback = None
        self._progress_callback = None
        self.typing_queue = queue.Queue()
        
        # Store original clipboard content
        try:
            win32clipboard.OpenClipboard()
            self.original_clipboard = win32clipboard.GetClipboardData(win32con.CF_UNICODETEXT) if win32clipboard.IsClipboardFormatAvailable(win32con.CF_UNICODETEXT) else ""
            win32clipboard.CloseClipboard()
        except:
            self.original_clipboard = ""

    def set_status_callback(self, callback: Callable[[str], None]) -> None:
        """Set callback for status updates."""
        self._status_callback = callback

    def set_progress_callback(self, callback: Callable[[int, int], None]) -> None:
        """Set callback for progress updates."""
        self._progress_callback = callback

    def cleanup(self):
        """Clean up resources safely."""
        self.running = False
        self.paused = False
        while not self.typing_queue.empty():
            try:
                self.typing_queue.get_nowait()
            except queue.Empty:
                break
        
        # Restore original clipboard content
        try:
            self.set_clipboard(self.original_clipboard)
        except:
            pass

    def set_text(self, text: str) -> None:
        """Set the text to be typed with preprocessing."""
        self.text = text
        self._prepare_typing_queue()

    def _prepare_typing_queue(self):
        """Pre-process text into typing chunks."""
        while not self.typing_queue.empty():
            self.typing_queue.get_nowait()
        
        # Process text character by character
        for char in self.text:
            self.typing_queue.put(char)

    def set_wpm(self, wpm: int) -> None:
        """Set typing speed in words per minute with validation."""
        self.wpm = max(1, min(wpm, 1000))

    def set_random_delay(self, enabled: bool, min_delay: float, max_delay: float) -> None:
        """Set random delay settings with validation."""
        min_delay = max(0.0, min_delay)
        max_delay = max(min_delay, max_delay)
        self.random_delay = {
            "enabled": enabled,
            "min": min_delay / 1000.0,
            "max": max_delay / 1000.0
        }

    def calculate_delay(self) -> float:
        """Calculate delay between keystrokes."""
        base_delay = 60.0 / (self.wpm * 5)  # Base delay from WPM
        
        # Add randomness if enabled
        if self.random_delay["enabled"]:
            variance = random.uniform(self.random_delay["min"], self.random_delay["max"])
            base_delay += variance
        
        return base_delay

    def update_status(self, status: str) -> None:
        """Thread-safe status update."""
        if self._status_callback:
            self._status_callback(status)

    def update_progress(self, current: int, total: int) -> None:
        """Thread-safe progress update."""
        if self._progress_callback:
            self._progress_callback(current, total)

    def set_clipboard(self, text: str) -> None:
        """Set text to clipboard with UTF-16 encoding for Thai support."""
        try:
            win32clipboard.OpenClipboard()
            win32clipboard.EmptyClipboard()
            win32clipboard.SetClipboardData(win32con.CF_UNICODETEXT, text)
        finally:
            win32clipboard.CloseClipboard()

    def type_text(self) -> None:
        """Type text using clipboard for Thai support."""
        try:
            self._countdown_start()
            
            total_chars = len(self.text)
            chars_typed = 0
            
            while self.running and not self.typing_queue.empty():
                if self.paused:
                    time.sleep(0.1)
                    continue

                char = self.typing_queue.get()
                
                # Handle spaces and Thai characters differently
                if char == ' ':
                    keyboard.press_and_release('space')
                else:
                    # Use clipboard for Thai characters
                    self.set_clipboard(char)
                    keyboard.press_and_release('ctrl+v')
                
                chars_typed += 1
                self.update_progress(chars_typed, total_chars)
                
                delay = self.calculate_delay()
                time.sleep(delay)
                
                if self.interval > 0 and self.typing_queue.empty():
                    self.update_status(f"Waiting {self.interval} seconds...")
                    time.sleep(self.interval)
                    self._prepare_typing_queue()

        except Exception as e:
            self.update_status(f"Error: {str(e)}")
        finally:
            self.cleanup()
            self.update_status("Completed" if chars_typed >= total_chars else "Stopped")

    def _countdown_start(self):
        """Handle countdown with status updates."""
        for i in range(3, 0, -1):
            if not self.running:
                return
            self.update_status(f"Starting in {i} seconds...")
            time.sleep(1)

    def start(self) -> None:
        """Start typing with proper thread management."""
        if not self.running and self.text:
            self.running = True
            self.paused = False
            self._prepare_typing_queue()
            self.thread = threading.Thread(target=self.type_text)
            self.thread.daemon = True
            self.thread.start()

    def stop(self) -> None:
        """Stop typing with proper cleanup."""
        self.running = False
        self.paused = False
        self.update_status("Stopped")

    def toggle_pause(self) -> None:
        """Toggle pause state with status update."""
        if self.running:
            self.paused = not self.paused
            self.update_status("Paused" if self.paused else "Resumed")

    def is_running(self) -> bool:
        """Check if typing is in progress."""
        return self.running

    def is_paused(self) -> bool:
        """Check if typing is paused."""
        return self.paused
