import json
import os
from pathlib import Path
from datetime import datetime
from typing import Dict, Optional, List

from config import PROFILES_DIR

class ProfileManager:
    def __init__(self):
        """Initialize the profile manager."""
        self.profiles_dir = PROFILES_DIR
        self.current_profile: Optional[Dict] = None
        self.current_profile_name: Optional[str] = None

    def save_profile(self, name: str, data: Dict) -> bool:
        """
        Save a typing profile to JSON file.
        
        Args:
            name: Profile name
            data: Profile data dictionary
        
        Returns:
            bool: True if save successful, False otherwise
        """
        try:
            # Sanitize filename
            safe_name = "".join(x for x in name if x.isalnum() or x in "._- ")
            filename = f"{safe_name}.json"
            filepath = self.profiles_dir / filename

            # Add metadata
            data['last_modified'] = datetime.now().isoformat()
            data['name'] = name

            with open(filepath, 'w') as f:
                json.dump(data, f, indent=4)
            
            self.current_profile = data
            self.current_profile_name = name
            return True
        except Exception as e:
            print(f"Error saving profile: {e}")
            return False

    def load_profile(self, name: str) -> Optional[Dict]:
        """
        Load a typing profile from JSON file.
        
        Args:
            name: Profile name
        
        Returns:
            Optional[Dict]: Profile data if successful, None otherwise
        """
        try:
            filename = f"{name}.json"
            filepath = self.profiles_dir / filename

            if not filepath.exists():
                return None

            with open(filepath, 'r') as f:
                data = json.load(f)
            
            self.current_profile = data
            self.current_profile_name = name
            return data
        except Exception as e:
            print(f"Error loading profile: {e}")
            return None

    def delete_profile(self, name: str) -> bool:
        """
        Delete a profile.
        
        Args:
            name: Profile name
        
        Returns:
            bool: True if deletion successful, False otherwise
        """
        try:
            filename = f"{name}.json"
            filepath = self.profiles_dir / filename

            if filepath.exists():
                os.remove(filepath)
                if self.current_profile_name == name:
                    self.current_profile = None
                    self.current_profile_name = None
                return True
            return False
        except Exception as e:
            print(f"Error deleting profile: {e}")
            return False

    def list_profiles(self) -> List[str]:
        """
        Get list of available profiles.
        
        Returns:
            List[str]: List of profile names
        """
        try:
            profiles = []
            for file in self.profiles_dir.glob("*.json"):
                profiles.append(file.stem)
            return sorted(profiles)
        except Exception as e:
            print(f"Error listing profiles: {e}")
            return []

    def create_new_profile(self, name: str) -> Dict:
        """
        Create a new empty profile template.
        
        Args:
            name: Profile name
        
        Returns:
            Dict: Empty profile template
        """
        return {
            "name": name,
            "created": datetime.now().isoformat(),
            "last_modified": datetime.now().isoformat(),
            "settings": {
                "wpm": 60,
                "random_delay": {
                    "enabled": False,
                    "min": 0.1,
                    "max": 1.0
                },
                "interval": 0.0
            },
            "texts": []
        }

    def get_current_profile(self) -> Optional[Dict]:
        """
        Get currently loaded profile.
        
        Returns:
            Optional[Dict]: Current profile data or None
        """
        return self.current_profile

    def get_current_profile_name(self) -> Optional[str]:
        """
        Get currently loaded profile name.
        
        Returns:
            Optional[str]: Current profile name or None
        """
        return self.current_profile_name
