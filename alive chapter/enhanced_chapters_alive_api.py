# backend/api/enhanced_chapters_alive_api.py
"""
Enhanced Chapters API with Alive Chapter Features
Integrates behavioral learning, Q&A, citations, and intelligent merging
"""

from fastapi import APIRouter, Depends, HTTPException, status, BackgroundTasks
from typing import Dict, List, Optional, Any
from pydantic import BaseModel
from datetime import datetime
import asyncio
import logging

# Import the alive chapter engines
import sys
import os
sys.path.append(os.path.join(os.path.dirname(__file__), '..', 'core'))

from chapter_behavioral_learning import chapter_behavioral_learning
from chapter_qa_engine import chapter_qa_engine
from citation_network_engine import citation_network_engine
from enhanced_nuance_merge_engine import enhanced_nuance_merge

# Import existing modules from NOr codebase
# from core.dependencies import get_current_user, CurrentUser
# from core.contextual_intelligence import contextual_intelligence
# from core.predictive_intelligence import predictive_intelligence
# from core.knowledge_graph import knowledge_graph
# from core.enhanced_research_engine import research_engine

router = APIRouter(prefix="/api/v1/alive-chapters", tags=["alive-chapters"])
logger = logging.getLogger(__name__)

# ============================================================================
# REQUEST/RESPONSE MODELS
# ============================================================================

class ChapterQARequest(BaseModel):
    """Request for in-chapter Q&A"""
    question: str
    chapter_id: str
    chapter_content: str
    section_context: Optional[str] = ""
    urgency: int = 3  # 1-5 scale

class AnticipateNeedsRequest(BaseModel):
    """Request for knowledge anticipation"""
    chapter_id: str
    chapter_content: str
    current_section: Optional[str] = None
    user_questions: Optional[List[str]] = []

class LearnInteractionRequest(BaseModel):
    """Request to learn from user interaction"""
    interaction_type: str  # read, edit, search, question, etc.
    chapter_id: str
    context_before: str
    context_after: Optional[str] = None
    duration: float = 0
    metadata: Dict[str, Any] = {}

class CitationNetworkRequest(BaseModel):
    """Request for citation network operations"""
    chapter_id: str
    chapter_content: str
    operation: str  # build, detect, suggest, visualize

class IntelligentMergeRequest(BaseModel):
    """Request for intelligent content merge"""
    chapter_id: str
    chapter_content: str
    new_knowledge: Dict[str, Any]
    integration_type: str  # qa_answer, anticipated, external_search
    auto_apply: bool = False

# ============================================================================
# Q&A ENDPOINTS
# ============================================================================

@router.post("/ask")
async def ask_question_in_chapter(
    request: ChapterQARequest,
    background_tasks: BackgroundTasks,
    user_id: str = "default_user"  # Would get from dependencies
):
    """
    Process a question within chapter context with AI search and integration
    """
    try:
        logger.info(f"Processing question for chapter {request.chapter_id}: {request.question}")

        # Process question through Q&A engine
        qa_result = await chapter_qa_engine.process_in_chapter_question(
            question=request.question,
            chapter_id=request.chapter_id,
            chapter_content=request.chapter_content,
            section_context=request.section_context or request.chapter_content[:500],
            user_id=user_id
        )

        if qa_result.get("status") != "success":
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=qa_result.get("message", "Q&A processing failed")
            )

        # Integrate answer into chapter using enhanced nuance merge
        if qa_result.get("auto_approved", False):
            merge_result = await enhanced_nuance_merge.merge_qa_answer(
                chapter_content=request.chapter_content,
                qa_answer=qa_result,
                chapter_id=request.chapter_id,
                user_id=user_id
            )

            # Update chapter content if merge successful
            if merge_result.get("status") == "success":
                qa_result["integrated_chapter"] = merge_result.get("content")
                qa_result["integration_analysis"] = merge_result.get("nuance_analysis")

        # Background task: Learn from this Q&A interaction
        background_tasks.add_task(
            _background_learning,
            user_id=user_id,
            chapter_id=request.chapter_id,
            interaction_type="question",
            metadata={"question": request.question, "answer": qa_result.get("answer")}
        )

        return {
            "status": "success",
            "question": request.question,
            "answer": qa_result.get("answer"),
            "integrated_chapter": qa_result.get("integrated_chapter"),
            "sources": qa_result.get("sources", []),
            "confidence": qa_result.get("confidence", 0),
            "integration_strategy": qa_result.get("integration_strategy"),
            "auto_integrated": qa_result.get("auto_approved", False),
            "quality_metrics": qa_result.get("quality_metrics", {}),
            "processing_time_ms": qa_result.get("processing_time_ms", 0)
        }

    except Exception as e:
        logger.error(f"Error processing question: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=str(e)
        )

# ============================================================================
# BEHAVIORAL LEARNING ENDPOINTS
# ============================================================================

@router.post("/learn")
async def learn_from_interaction(
    request: LearnInteractionRequest,
    user_id: str = "default_user"
):
    """
    Learn from user interaction to improve chapter intelligence
    """
    try:
        # Learn from interaction
        learning_result = await chapter_behavioral_learning.learn_from_interaction({
            "user_id": user_id,
            "chapter_id": request.chapter_id,
            "type": request.interaction_type,
            "context_before": request.context_before,
            "context_after": request.context_after,
            "duration": request.duration,
            "metadata": request.metadata,
            "session_id": f"session_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
        })

        return {
            "status": learning_result.get("status"),
            "interaction_id": learning_result.get("interaction_id"),
            "patterns_detected": learning_result.get("patterns_detected", 0),
            "confidence": learning_result.get("confidence", 0)
        }

    except Exception as e:
        logger.error(f"Error learning from interaction: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=str(e)
        )

@router.post("/anticipate")
async def anticipate_knowledge_needs(
    request: AnticipateNeedsRequest,
    background_tasks: BackgroundTasks,
    user_id: str = "default_user"
):
    """
    Anticipate what knowledge the user will need next
    """
    try:
        # Prepare context
        chapter_context = {
            "chapter_id": request.chapter_id,
            "user_id": user_id,
            "content": request.chapter_content,
            "current_section": request.current_section,
            "user_questions": request.user_questions
        }

        # Get anticipated needs
        anticipation_result = await chapter_behavioral_learning.anticipate_knowledge_needs(
            chapter_context
        )

        if anticipation_result.get("status") != "success":
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Anticipation failed"
            )

        # Auto-fill high-confidence gaps if requested
        anticipated_needs = anticipation_result.get("anticipated_needs", [])
        knowledge_gaps = anticipation_result.get("knowledge_gaps", [])

        # Background task: Prefetch anticipated knowledge
        background_tasks.add_task(
            _background_prefetch,
            anticipated_needs=anticipated_needs[:5],
            chapter_id=request.chapter_id
        )

        # Optionally merge anticipated knowledge
        enhanced_content = None
        if anticipated_needs and anticipated_needs[0].get("confidence", 0) > 0.8:
            merge_result = await enhanced_nuance_merge.merge_anticipated_knowledge(
                chapter_content=request.chapter_content,
                anticipated_needs=anticipated_needs,
                chapter_id=request.chapter_id,
                user_id=user_id
            )
            enhanced_content = merge_result.get("content")

        return {
            "status": "success",
            "anticipated_needs": anticipated_needs,
            "knowledge_gaps": knowledge_gaps,
            "user_preferences": anticipation_result.get("user_preferences", {}),
            "learning_confidence": anticipation_result.get("learning_confidence", 0),
            "enhanced_content": enhanced_content,
            "prefetching_started": len(anticipated_needs) > 0
        }

    except Exception as e:
        logger.error(f"Error anticipating needs: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=str(e)
        )

@router.get("/suggestions/{chapter_id}")
async def get_proactive_suggestions(
    chapter_id: str,
    user_id: str = "default_user"
):
    """
    Get proactive suggestions based on behavioral learning
    """
    try:
        suggestions = await chapter_behavioral_learning.get_proactive_suggestions(
            chapter_id=chapter_id,
            user_id=user_id
        )

        return {
            "status": "success",
            "chapter_id": chapter_id,
            "suggestions": suggestions,
            "total_suggestions": len(suggestions)
        }

    except Exception as e:
        logger.error(f"Error getting suggestions: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=str(e)
        )

# ============================================================================
# CITATION NETWORK ENDPOINTS
# ============================================================================

@router.post("/citations")
async def manage_citation_network(
    request: CitationNetworkRequest,
    user_id: str = "default_user"
):
    """
    Manage citation network and cross-references
    """
    try:
        result = {}

        if request.operation == "detect":
            # Detect cross-references
            cross_refs = await citation_network_engine.detect_cross_references(
                chapter_content=request.chapter_content,
                chapter_id=request.chapter_id
            )

            result = {
                "status": "success",
                "operation": "detect",
                "cross_references": [
                    {
                        "reference_id": ref.reference_id,
                        "to_resource": ref.to_resource,
                        "reference_type": ref.reference_type.value,
                        "relevance_score": ref.relevance_score,
                        "medical_concepts": ref.medical_concepts
                    }
                    for ref in cross_refs
                ],
                "total_references": len(cross_refs)
            }

        elif request.operation == "suggest":
            # Suggest citations
            suggestions = await citation_network_engine.suggest_citations(
                current_context=request.chapter_content[:1000],  # First 1000 chars
                chapter_id=request.chapter_id
            )

            result = {
                "status": "success",
                "operation": "suggest",
                "suggestions": suggestions,
                "total_suggestions": len(suggestions)
            }

        elif request.operation == "visualize":
            # Visualize network
            visualization = await citation_network_engine.visualize_citation_network(
                chapter_id=request.chapter_id
            )

            result = {
                "status": "success",
                "operation": "visualize",
                "visualization": visualization
            }

        elif request.operation == "apply":
            # Apply citations to chapter
            applied_result = await enhanced_nuance_merge.apply_citation_network(
                chapter_content=request.chapter_content,
                chapter_id=request.chapter_id,
                all_chapters=[]  # Would fetch from database
            )

            result = {
                "status": "success",
                "operation": "apply",
                "updated_content": applied_result.get("content"),
                "citations_added": applied_result.get("citations_added", 0),
                "cross_references_detected": applied_result.get("cross_references_detected", 0)
            }

        else:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Invalid operation: {request.operation}"
            )

        return result

    except Exception as e:
        logger.error(f"Error managing citations: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=str(e)
        )

@router.get("/citations/stats/{chapter_id}")
async def get_citation_statistics(
    chapter_id: str
):
    """
    Get citation statistics for a chapter
    """
    try:
        stats = await citation_network_engine.get_citation_statistics(chapter_id)

        return {
            "status": "success",
            "statistics": stats
        }

    except Exception as e:
        logger.error(f"Error getting citation stats: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=str(e)
        )

# ============================================================================
# INTELLIGENT MERGE ENDPOINTS
# ============================================================================

@router.post("/merge")
async def intelligent_merge(
    request: IntelligentMergeRequest,
    background_tasks: BackgroundTasks,
    user_id: str = "default_user"
):
    """
    Perform intelligent merge of new knowledge into chapter
    """
    try:
        # Prepare integration context
        integration_context = {
            "integration_type": request.integration_type,
            "auto_apply": request.auto_apply,
            "timestamp": datetime.now().isoformat()
        }

        # Perform intelligent merge
        merge_result = await enhanced_nuance_merge.intelligent_knowledge_integration(
            chapter_content=request.chapter_content,
            new_knowledge=request.new_knowledge,
            chapter_id=request.chapter_id,
            user_id=user_id,
            integration_context=integration_context
        )

        # Background task: Update citation network
        if merge_result.get("status") == "success":
            background_tasks.add_task(
                _update_citation_network,
                chapter_id=request.chapter_id,
                content=merge_result.get("content")
            )

        return {
            "status": merge_result.get("status"),
            "merged_content": merge_result.get("content"),
            "nuance_analysis": merge_result.get("nuance_analysis"),
            "integration_points": merge_result.get("integration_points"),
            "conflicts_resolved": merge_result.get("conflicts_resolved", 0),
            "citations_added": merge_result.get("citations_added", 0),
            "quality_metrics": merge_result.get("quality_metrics", {})
        }

    except Exception as e:
        logger.error(f"Error performing merge: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=str(e)
        )

# ============================================================================
# CHAPTER HEALTH ENDPOINTS
# ============================================================================

@router.get("/health/{chapter_id}")
async def get_chapter_health(
    chapter_id: str,
    user_id: str = "default_user"
):
    """
    Get comprehensive health metrics for an alive chapter
    """
    try:
        # Get Q&A history
        qa_history = await chapter_qa_engine.get_qa_history(chapter_id)

        # Get citation stats
        citation_stats = await citation_network_engine.get_citation_statistics(chapter_id)

        # Get behavioral insights
        suggestions = await chapter_behavioral_learning.get_proactive_suggestions(
            chapter_id, user_id
        )

        # Calculate health metrics
        health_metrics = {
            "chapter_id": chapter_id,
            "last_updated": datetime.now().isoformat(),
            "qa_activity": {
                "total_questions": len(qa_history),
                "avg_confidence": sum(q.get("confidence", 0) for q in qa_history) / len(qa_history) if qa_history else 0
            },
            "citation_health": {
                "incoming_citations": citation_stats.get("incoming_citations", 0),
                "outgoing_citations": citation_stats.get("outgoing_citations", 0),
                "centrality_score": citation_stats.get("centrality_score", 0)
            },
            "behavioral_insights": {
                "suggestions_available": len(suggestions),
                "learning_confidence": suggestions[0].get("confidence", 0) if suggestions else 0
            },
            "overall_health_score": 0.0
        }

        # Calculate overall health score
        scores = [
            health_metrics["qa_activity"]["avg_confidence"],
            health_metrics["citation_health"]["centrality_score"],
            health_metrics["behavioral_insights"]["learning_confidence"]
        ]
        health_metrics["overall_health_score"] = sum(scores) / len(scores) if scores else 0

        return {
            "status": "success",
            "health_metrics": health_metrics
        }

    except Exception as e:
        logger.error(f"Error getting chapter health: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=str(e)
        )

# ============================================================================
# BACKGROUND TASKS
# ============================================================================

async def _background_learning(user_id: str, chapter_id: str,
                              interaction_type: str, metadata: Dict[str, Any]):
    """Background task for learning from interactions"""
    try:
        await chapter_behavioral_learning.learn_from_interaction({
            "user_id": user_id,
            "chapter_id": chapter_id,
            "type": interaction_type,
            "metadata": metadata,
            "timestamp": datetime.now()
        })
        logger.info(f"Background learning completed for {chapter_id}")
    except Exception as e:
        logger.error(f"Background learning failed: {e}")

async def _background_prefetch(anticipated_needs: List[Dict[str, Any]],
                              chapter_id: str):
    """Background task for prefetching anticipated knowledge"""
    try:
        for need in anticipated_needs:
            # Simulate prefetching (would integrate with research engines)
            logger.info(f"Prefetching knowledge for {need.get('type')} in chapter {chapter_id}")
            await asyncio.sleep(1)  # Simulate processing
        logger.info(f"Prefetching completed for chapter {chapter_id}")
    except Exception as e:
        logger.error(f"Prefetching failed: {e}")

async def _update_citation_network(chapter_id: str, content: str):
    """Background task to update citation network"""
    try:
        await citation_network_engine.detect_cross_references(content, chapter_id)
        logger.info(f"Citation network updated for chapter {chapter_id}")
    except Exception as e:
        logger.error(f"Citation network update failed: {e}")

# ============================================================================
# COMPOSITE ENDPOINTS
# ============================================================================

@router.post("/evolve/{chapter_id}")
async def evolve_chapter(
    chapter_id: str,
    chapter_content: str,
    background_tasks: BackgroundTasks,
    user_id: str = "default_user"
):
    """
    Comprehensive chapter evolution: anticipate, search, merge, and enhance
    """
    try:
        logger.info(f"Starting comprehensive evolution for chapter {chapter_id}")

        # Step 1: Anticipate needs
        anticipation_result = await chapter_behavioral_learning.anticipate_knowledge_needs({
            "chapter_id": chapter_id,
            "user_id": user_id,
            "content": chapter_content
        })

        anticipated_needs = anticipation_result.get("anticipated_needs", [])
        knowledge_gaps = anticipation_result.get("knowledge_gaps", [])

        # Step 2: Fill top knowledge gaps
        enhanced_content = chapter_content
        enhancements_applied = []

        for gap in knowledge_gaps[:3]:  # Top 3 gaps
            if gap.get("auto_fillable") and gap.get("confidence", 0) > 0.7:
                # Would search for knowledge to fill gap
                # For now, simulate with placeholder
                new_knowledge = {
                    "content": f"Knowledge to fill gap: {gap.get('description')}",
                    "sources": [{"title": "Auto-filled", "source": "System"}],
                    "confidence": gap.get("confidence", 0.5)
                }

                # Merge knowledge
                merge_result = await enhanced_nuance_merge.intelligent_knowledge_integration(
                    chapter_content=enhanced_content,
                    new_knowledge=new_knowledge,
                    chapter_id=chapter_id,
                    user_id=user_id,
                    integration_context={"type": "gap_filling"}
                )

                if merge_result.get("status") == "success":
                    enhanced_content = merge_result.get("content", enhanced_content)
                    enhancements_applied.append({
                        "gap_type": gap.get("type"),
                        "confidence": gap.get("confidence"),
                        "applied": True
                    })

        # Step 3: Apply citations
        citation_result = await enhanced_nuance_merge.apply_citation_network(
            chapter_content=enhanced_content,
            chapter_id=chapter_id,
            all_chapters=[]  # Would fetch from database
        )

        final_content = citation_result.get("content", enhanced_content)

        # Step 4: Calculate evolution metrics
        evolution_metrics = {
            "anticipated_needs": len(anticipated_needs),
            "gaps_filled": len(enhancements_applied),
            "citations_added": citation_result.get("citations_added", 0),
            "content_growth": len(final_content) / len(chapter_content) if chapter_content else 1.0,
            "evolution_confidence": sum(e.get("confidence", 0) for e in enhancements_applied) / len(enhancements_applied) if enhancements_applied else 0
        }

        # Background tasks
        background_tasks.add_task(
            _background_learning,
            user_id=user_id,
            chapter_id=chapter_id,
            interaction_type="evolution",
            metadata=evolution_metrics
        )

        return {
            "status": "success",
            "chapter_id": chapter_id,
            "evolved_content": final_content,
            "evolution_metrics": evolution_metrics,
            "enhancements_applied": enhancements_applied,
            "anticipated_needs": anticipated_needs[:5],  # Top 5
            "knowledge_gaps_filled": len(enhancements_applied)
        }

    except Exception as e:
        logger.error(f"Error evolving chapter: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=str(e)
        )

# Export router
__all__ = ["router"]