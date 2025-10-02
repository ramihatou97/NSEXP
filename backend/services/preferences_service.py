"""
User Preferences Service
Handles user settings and preferences
"""

import logging

logger = logging.getLogger(__name__)

# Default preferences
DEFAULT_PREFERENCES = {
    "ai_settings": {
        "default_model": "openai",
        "temperature": 0.7,
        "max_tokens": 2000,
        "enable_citations": True
    },
    "display_settings": {
        "theme": "auto",
        "font_size": "medium",
        "compact_mode": False,
        "show_preview": True
    },
    "default_settings": {
        "specialty": "Neurosurgery General",
        "language": "en",
        "citation_style": "vancouver"
    },
    "notification_settings": {
        "email_notifications": False,
        "synthesis_complete": True,
        "gap_detection": True
    }
}

# In-memory storage (for single-user simplified version)
_user_preferences = DEFAULT_PREFERENCES.copy()


async def get_user_preferences():
    """Get user preferences"""
    logger.info("Retrieving user preferences")
    return {
        "success": True,
        "data": _user_preferences
    }


async def update_user_preferences(preferences: dict):
    """Update user preferences"""
    global _user_preferences

    logger.info(f"Updating user preferences: {list(preferences.keys())}")

    # Deep update preferences
    for section_key, section_value in preferences.items():
        if section_key in _user_preferences and isinstance(section_value, dict):
            _user_preferences[section_key].update(section_value)
        else:
            _user_preferences[section_key] = section_value

    return {
        "success": True,
        "data": _user_preferences,
        "message": "Preferences updated successfully"
    }
