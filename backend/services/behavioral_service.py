"""
Behavioral Learning Service
Tracks user behavior and generates personalized suggestions
"""

import logging
from datetime import datetime, timezone
from typing import List, Dict, Any
from collections import defaultdict, Counter

logger = logging.getLogger(__name__)

# In-memory storage for user actions
_user_actions: List[Dict[str, Any]] = []
_action_counts = defaultdict(int)
_specialty_counts = Counter()
_topic_counts = Counter()


async def track_action(action_type: str, context: dict):
    """Track user action for behavioral learning"""
    logger.info(f"Tracking action: {action_type}")

    action = {
        "action_type": action_type,
        "context": context,
        "timestamp": datetime.now(timezone.utc).isoformat()
    }

    _user_actions.append(action)
    _action_counts[action_type] += 1

    # Track specialty interest
    if "specialty" in context:
        _specialty_counts[context["specialty"]] += 1

    # Track topic interest
    if "query" in context:
        _topic_counts[context["query"]] += 1


async def get_personalized_suggestions():
    """Generate personalized suggestions based on user behavior"""
    logger.info("Generating personalized suggestions")

    suggestions = []

    # Get top specialties
    top_specialties = _specialty_counts.most_common(3)

    # Suggest chapters based on frequent specialties
    if top_specialties:
        for specialty, count in top_specialties:
            suggestions.append({
                "id": f"sug_{len(suggestions) + 1}",
                "type": "chapter",
                "title": f"Explore more {specialty} content",
                "description": f"Based on your {count} interactions with {specialty}",
                "relevance_score": min(count / 10.0, 1.0),
                "reason": f"You've shown interest in {specialty}",
                "action_url": f"/library?specialty={specialty}",
                "metadata": {"specialty": specialty}
            })

    # Suggest based on recent searches
    if _action_counts.get("search", 0) > 0:
        suggestions.append({
            "id": f"sug_{len(suggestions) + 1}",
            "type": "topic",
            "title": "Try AI-powered synthesis",
            "description": "Generate comprehensive chapters from your search topics",
            "relevance_score": 0.8,
            "reason": "You've been searching for information",
            "action_url": "/synthesis",
            "metadata": {}
        })

    # Suggest references if user has created chapters
    if _action_counts.get("create", 0) > 0:
        suggestions.append({
            "id": f"sug_{len(suggestions) + 1}",
            "type": "reference",
            "title": "Add references to your chapters",
            "description": "Build a comprehensive citation library",
            "relevance_score": 0.7,
            "reason": "You've created chapters recently",
            "action_url": "/references",
            "metadata": {}
        })

    # Always suggest procedures if not viewed yet
    if _action_counts.get("view_procedures", 0) == 0:
        suggestions.append({
            "id": f"sug_{len(suggestions) + 1}",
            "type": "procedure",
            "title": "Explore surgical procedures database",
            "description": "Browse step-by-step neurosurgical procedures",
            "relevance_score": 0.9,
            "reason": "New feature available",
            "action_url": "/procedures",
            "metadata": {}
        })

    # If no activity, suggest getting started
    if len(_user_actions) < 5:
        suggestions.append({
            "id": f"sug_{len(suggestions) + 1}",
            "type": "chapter",
            "title": "Start with AI synthesis",
            "description": "Generate your first neurosurgical chapter using AI",
            "relevance_score": 1.0,
            "reason": "Get started with the platform",
            "action_url": "/synthesis",
            "metadata": {}
        })

    return {
        "success": True,
        "data": suggestions[:5],  # Return top 5 suggestions
        "total": len(suggestions)
    }
