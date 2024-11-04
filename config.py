import json
import os
from pathlib import Path

# Application Constants
APP_NAME = "Auto Typer"
VERSION = "1.0.0"

# File Paths
BASE_DIR = Path(os.path.dirname(os.path.abspath(__file__)))
PROFILES_DIR = BASE_DIR / "profiles"
PROFILES_DIR.mkdir(exist_ok=True)

# Default Settings
DEFAULT_SETTINGS = {
    "theme": "light",
    "wpm": 60,
    "random_delay": {
        "enabled": False,
        "min": 100,  # 100 milliseconds
        "max": 1000  # 1000 milliseconds
    },
    "interval": 0.0,
    "failsafe": True,
    "hotkeys": {
        "start_stop": "F6",
        "emergency_stop": "esc"
    }
}

# Theme configurations
THEMES = {
    "light": {
        "bg": "#ffffff",
        "fg": "#000000",
        "button": "#f0f0f0",
        "frame": "#e0e0e0",
        "highlight": "#0078d7"
    },
    "dark": {
        "bg": "#2d2d2d",
        "fg": "#ffffff",
        "button": "#3d3d3d",
        "frame": "#363636",
        "highlight": "#0078d7"
    }
}

# Status Messages
STATUS_MESSAGES = {
    "ready": "Ready",
    "typing": "Typing in progress...",
    "paused": "Paused",
    "stopped": "Stopped",
    "loading": "Loading...",
    "saving": "Saving...",
    "error": "Error occurred"
}

def load_settings():
    """Load application settings from config file."""
    settings_path = BASE_DIR / "settings.json"
    try:
        if settings_path.exists():
            with open(settings_path, 'r') as f:
                loaded_settings = json.load(f)
                # Merge with defaults to ensure all required fields exist
                merged_settings = DEFAULT_SETTINGS.copy()
                merged_settings.update(loaded_settings)
                return merged_settings
        return DEFAULT_SETTINGS
    except Exception:
        return DEFAULT_SETTINGS

def save_settings(settings):
    """Save application settings to config file."""
    settings_path = BASE_DIR / "settings.json"
    try:
        with open(settings_path, 'w') as f:
            json.dump(settings, f, indent=4)
        return True
    except Exception:
        return False
