"""
Configuration management for PTCC
Loads settings from config.yaml and provides typed access
"""

import os
import yaml
from pathlib import Path
from typing import Dict, List, Optional

# Default configuration
DEFAULT_CONFIG = {
    "school": {
        "name": "Your School Name",
        "campuses": [
            {"name": "Junior Campus", "code": "A"},
            {"name": "EYI Campus", "code": "B"}
        ],
        "year_groups": ["7", "8", "9", "10", "11"],
        "houses": []
    },
    "timetable": {
        "periods_per_day": 6,
        "start_time": "08:30",
        "period_length": 45,
        "break_times": [
            {"name": "Morning Break", "start": "10:30", "duration": "15"},
            {"name": "Lunch", "start": "12:15", "duration": "45"}
        ],
        "days": ["Monday", "Tuesday", "Wednesday", "Thursday", "Friday"]
    },
    "data": {
        "raw": "data/raw",
        "processed": "data/processed",
        "chroma": "data/chroma",
        "database": "data/school.db",
        "backups": "data/backups"
    },
    "file_paths": {
        "class_lists": "~/SchoolData/2025-26/students/",
        "assessments": "~/SchoolData/2025-26/assessments/",
        "meetings": "~/SchoolData/2025-26/meetings/",
        "emails": "~/SchoolData/2025-26/emails/",
        "timetables": "~/SchoolData/2025-26/timetables/",
        "rotas": "~/SchoolData/2025-26/rotas/",
        "student_photos": "~/SchoolData/2025-26/students/photos/"
    },
    "llm": {
        "models": {
            "gemini_default": "gemini-2.5-flash",
            "gemini_pro": "gemini-2.5-pro",
            "gemini_vision": "gemini-pro-vision"
        },
        "local": {
            "provider": "ollama",
            "model": "phi3:mini",
            "base_url": "http://localhost:11434"
        },
        "cloud": {
            "provider": "claude",
            "api_key": ""
        },
        "gemini": {
            "provider": "gemini"
        }
    },
    "system": {
        "debug": False,
        "log_level": "INFO",
        "auto_backup": True,
        "backup_time": "23:59",
        "max_search_results": 5
    },
    "security": {
        "password_required": False,
        "database_encryption": False
    },
    "mobile": {
        "enable_offline": True,
        "sync_interval": 30,
        "max_offline_logs": 1000
    },
    "briefing": {
        "show_student_count": True,
        "highlight_high_support": True,
        "show_recent_incidents": True,
        "days_to_check": 14,
        "max_incidents_per_student": 5
    },
    "search": {
        "default_top_k": 5,
        "rerank_results": False,
        "include_pdf_content": True,
        "include_email_content": True,
        "include_meeting_notes": True
    },
    "patterns": {
        "enabled": True,
        "check_frequency": "daily",
        "behavior_threshold": 3,
        "performance_drop_threshold": -15,
        "low_interaction_days": 14
    },
    "alerts": {
        "pre_lesson_reminder": True,
        "reminder_minutes": 10,
        "sound_enabled": False,
        "desktop_notifications": True
    },
    "flashcards": {
        "enabled": True,
        "daily_target": 10,
        "show_context_hints": True,
        "spaced_repetition": True
    },
    "import_settings": {
        "auto_detect_types": True,
        "create_backups": True,
        "validate_data": True,
        "max_file_size": "100MB"
    },
    "export": {
        "include_student_photos": False,
        "anonymize_data": False,
        "format": "json"
    }
}

# Global configuration instance
_config = None


def get_config_path():
    """Get the path to the configuration file"""
    # Try current directory first, then parent directories
    current_path = os.getcwd()

    # Look for config in ptcc/config/ if we're in the project root
    if os.path.basename(current_path) == "ptcc":
        config_path = os.path.join(current_path, "config", "config.yaml")
        if os.path.exists(config_path):
            return config_path

    # Look for config in current directory
    config_path = os.path.join(current_path, "config", "config.yaml")
    if os.path.exists(config_path):
        return config_path

    # Default to project config
    project_root = os.path.dirname(os.path.dirname(os.path.dirname(__file__)))
    config_path = os.path.join(project_root, "config", "config.yaml")
    return config_path


def load_config() -> Dict:
    """Load configuration from YAML file"""
    config_path = get_config_path()

    if not os.path.exists(config_path):
        print(f"Warning: Configuration file not found: {config_path}")
        print("Using default configuration")
        return DEFAULT_CONFIG.copy()

    try:
        with open(config_path, 'r') as f:
            user_config = yaml.safe_load(f) or {}

        # Merge with defaults
        config = DEFAULT_CONFIG.copy()
        for section, values in user_config.items():
            if section in config and isinstance(config[section], dict) and isinstance(values, dict):
                config[section].update(values)
            else:
                config[section] = values

        return config

    except Exception as e:
        print(f"Error loading configuration: {e}")
        print("Using default configuration")
        return DEFAULT_CONFIG.copy()


def get_settings() -> Dict:
    """Get the global settings instance"""
    global _config
    if _config is None:
        _config = load_config()
    return _config


def reload_settings():
    """Reload settings from file"""
    global _config
    _config = load_config()
    return _config


# Convenience functions for commonly used paths
def get_data_dir():
    """Get the data directory path"""
    return os.path.expanduser(get_settings()["data"]["raw"])


def get_database_path():
    """Get the database file path"""
    return os.path.expanduser(get_settings()["data"]["database"])


def get_chroma_path():
    """Get the ChromaDB directory path"""
    return os.path.expanduser(get_settings()["data"]["chroma"])


def get_student_photos_dir():
    """Get the student photos directory path"""
    return os.path.expanduser(get_settings()["file_paths"]["student_photos"])


# Convenience functions for commonly used paths (using Path objects)
def get_data_dir_path() -> Path:
    """Get the data directory path"""
    return Path(get_settings()["data"]["raw"]).expanduser()


def get_database_path_path() -> Path:
    """Get the database file path"""
    return Path(get_settings()["data"]["database"]).expanduser()


def get_chroma_path_path() -> Path:
    """Get the ChromaDB directory path"""
    return Path(get_settings()["data"]["chroma"]).expanduser()


def get_student_photos_dir_path() -> Path:
    """Get the student photos directory path"""
    return Path(get_settings()["file_paths"]["student_photos"]).expanduser()


def get_gemini_model(model_type: str = "default") -> str:
    """
    Get Gemini model ID from centralized config.
    
    Args:
        model_type: "default" (flash), "pro", or "vision"
    
    Returns:
        Model ID string
    """
    model_map = {
        "default": "gemini_default",
        "flash": "gemini_default",
        "pro": "gemini_pro",
        "vision": "gemini_vision"
    }
    
    key = model_map.get(model_type, "gemini_default")
    settings = get_settings()
    
    # Return from config if available, otherwise fallback defaults
    if "llm" in settings and "models" in settings["llm"]:
        return settings["llm"]["models"].get(key, DEFAULT_CONFIG["llm"]["models"][key])
    
    return DEFAULT_CONFIG["llm"]["models"][key]
