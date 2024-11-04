import threading
import time
import random
from typing import Optional, Callable
import pyautogui
import keyboard
from datetime import datetime, time as dt_time
from contextlib import contextmanager
import queue
import itertools

class AutoTyper:
    def __init__(self):
        """Initialize the AutoTyper with optimized settings."""
        self.running = False
        self.paused = False
        self.thread: Optional[threading.Thread] = None
        self.text = ""
        self.wpm = 60
        self.random_delay = {
            "enabled": False,
            "min": 100,
            "max": 1000
        }
        self.interval = 0.0
        self.scheduled_time: Optional[dt_time] = None
        self._status_callback: Optional[Callable[[str], None]] = None
        self._progress_callback: Optional[Callable[[int, int], None]] = None
        self.typing_queue = queue.Queue()
        
        # Optimize PyAutoGUI settings
        pyautogui.FAILSAFE = True
        pyautogui.PAUSE = 0.0
        
        # Natural typing patterns
        self.typing_patterns = {
            'common_pairs': {'th': 0.9, 'he': 0.9, 'in': 0.9, 'er': 0.9},
            'end_sentence': {'.': 1.2, '!': 1.2, '?': 1.2},
            'punctuation': {',': 1.1, ';': 1.1, ':': 1.1}
        }

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

    def set_text(self, text: str) -> None:
        """Set the text to be typed with preprocessing."""
        self.text = text
        self._prepare_typing_queue()

    def _prepare_typing_queue(self):
        """Pre-process text into optimized typing chunks."""
        while not self.typing_queue.empty():
            self.typing_queue.get_nowait()
        
        chunk_size = 10
        chunks = [''.join(chunk) for chunk in itertools.zip_longest(*[iter(self.text)]*chunk_size, fillvalue='')]
        for chunk in chunks:
            self.typing_queue.put(chunk)

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

    def calculate_delay(self, current_char: str, next_char: Optional[str] = None) -> float:
        """Calculate intelligent delay between keystrokes."""
        base_delay = 60.0 / (self.wpm * 5)  # Base delay from WPM
        
        # Apply natural typing patterns
        if next_char and current_char + next_char in self.typing_patterns['common_pairs']:
            base_delay *= self.typing_patterns['common_pairs'][current_char + next_char]
        elif current_char in self.typing_patterns['end_sentence']:
            base_delay *= self.typing_patterns['end_sentence'][current_char]
        elif current_char in self.typing_patterns['punctuation']:
            base_delay *= self.typing_patterns['punctuation'][current_char]
        
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

    def type_text(self) -> None:
        """Optimized typing function with better performance."""
        try:
            self._countdown_start()
            
            total_chars = len(self.text)
            chars_typed = 0
            
            while self.running and not self.typing_queue.empty():
                if self.paused:
                    time.sleep(0.1)
                    continue

                chunk = self.typing_queue.get()
                pyautogui.write(chunk)  # Batch typing for better performance
                
                chars_typed += len(chunk)
                self.update_progress(chars_typed, total_chars)
                
                # Calculate delay after chunk
                delay = self.calculate_delay(chunk[-1], 
                                          self.text[chars_typed] if chars_typed < total_chars else None)
                time.sleep(delay)
                
                if self.interval > 0 and self.typing_queue.empty():
                    self.update_status(f"Waiting {self.interval} seconds...")
                    time.sleep(self.interval)
                    self._prepare_typing_queue()  # Prepare for next iteration

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
