"""
Conceptual Map Service
Generates comprehensive knowledge graphs showing relationships between chapters, 
references, procedures, and anatomical regions in the neurosurgical knowledge base.
"""

import logging
from typing import List, Dict, Any, Optional
from collections import defaultdict
import uuid

logger = logging.getLogger(__name__)


async def get_full_conceptual_map(
    specialty: Optional[str] = None,
    anatomical_region: Optional[str] = None,
    procedure_type: Optional[str] = None,
    include_references: bool = True,
    include_procedures: bool = True,
    max_nodes: int = 100
) -> Dict[str, Any]:
    """
    Generate comprehensive conceptual map of neurosurgical knowledge
    
    Args:
        specialty: Filter by neurosurgical specialty (e.g., 'tumor', 'vascular')
        anatomical_region: Filter by anatomical region
        procedure_type: Filter by procedure type
        include_references: Include reference nodes in the graph
        include_procedures: Include procedure nodes in the graph
        max_nodes: Maximum number of nodes to include
        
    Returns:
        Dict containing nodes and edges for the conceptual map
    """
    logger.info(
        f"Generating conceptual map - specialty: {specialty}, "
        f"region: {anatomical_region}, procedure: {procedure_type}"
    )
    
    # Mock data - In production, this would query the database
    # Generate chapters
    chapters = _generate_sample_chapters(specialty, anatomical_region, max_nodes // 2)
    
    # Generate references
    references = []
    if include_references:
        references = _generate_sample_references(max_nodes // 4)
    
    # Generate procedures
    procedures = []
    if include_procedures:
        procedures = _generate_sample_procedures(procedure_type, max_nodes // 4)
    
    # Build nodes
    nodes = []
    
    # Add chapter nodes
    for chapter in chapters:
        nodes.append({
            "id": chapter["id"],
            "label": chapter["title"],
            "type": "chapter",
            "specialty": chapter["specialty"],
            "anatomical_region": chapter.get("anatomical_region"),
            "size": 8,
            "color": _get_color_for_type("chapter"),
            "metadata": {
                "topic": chapter.get("topic"),
                "completeness_score": chapter.get("completeness_score", 0.8),
                "reference_count": chapter.get("reference_count", 0)
            }
        })
    
    # Add reference nodes
    for ref in references:
        nodes.append({
            "id": ref["id"],
            "label": ref["title"],
            "type": "reference",
            "year": ref.get("year"),
            "size": 5,
            "color": _get_color_for_type("reference"),
            "metadata": {
                "authors": ref.get("authors", []),
                "citation_count": ref.get("citation_count", 0),
                "evidence_level": ref.get("evidence_level")
            }
        })
    
    # Add procedure nodes
    for proc in procedures:
        nodes.append({
            "id": proc["id"],
            "label": proc["name"],
            "type": "procedure",
            "procedure_type": proc.get("procedure_type"),
            "size": 6,
            "color": _get_color_for_type("procedure"),
            "metadata": {
                "anatomical_region": proc.get("anatomical_region"),
                "complexity": proc.get("complexity"),
                "success_rate": proc.get("success_rate")
            }
        })
    
    # Build edges (relationships)
    edges = []
    
    # Chapter-Reference relationships
    for chapter in chapters:
        for ref_id in chapter.get("reference_ids", [])[:3]:  # Limit to 3 references per chapter
            edges.append({
                "source": chapter["id"],
                "target": ref_id,
                "type": "cites",
                "weight": 1,
                "label": "cites"
            })
    
    # Chapter-Procedure relationships
    for chapter in chapters:
        for proc_id in chapter.get("procedure_ids", [])[:2]:  # Limit to 2 procedures per chapter
            edges.append({
                "source": chapter["id"],
                "target": proc_id,
                "type": "discusses",
                "weight": 1,
                "label": "discusses"
            })
    
    # Chapter-Chapter relationships (related topics)
    for i, chapter1 in enumerate(chapters):
        for chapter2 in chapters[i+1:i+3]:  # Connect to 2 nearby chapters
            if _are_related(chapter1, chapter2):
                edges.append({
                    "source": chapter1["id"],
                    "target": chapter2["id"],
                    "type": "related",
                    "weight": 0.5,
                    "label": "related"
                })
    
    # Reference-Reference relationships (co-citations)
    for i, ref1 in enumerate(references[:10]):  # Limit for performance
        for ref2 in references[i+1:i+3]:
            if ref1.get("year") == ref2.get("year"):
                edges.append({
                    "source": ref1["id"],
                    "target": ref2["id"],
                    "type": "co-cited",
                    "weight": 0.3,
                    "label": "co-cited"
                })
    
    # Calculate statistics
    stats = {
        "total_nodes": len(nodes),
        "total_edges": len(edges),
        "node_types": _count_by_type(nodes),
        "edge_types": _count_by_type(edges, key="type"),
        "specialties": _count_by_type(nodes, key="specialty"),
        "anatomical_regions": _count_by_type(nodes, key="anatomical_region")
    }
    
    return {
        "success": True,
        "data": {
            "nodes": nodes,
            "edges": edges,
            "statistics": stats,
            "filters_applied": {
                "specialty": specialty,
                "anatomical_region": anatomical_region,
                "procedure_type": procedure_type
            }
        }
    }


async def search_concepts(
    query: str,
    map_type: str = "all"
) -> Dict[str, Any]:
    """
    Search for concepts in the knowledge graph
    
    Args:
        query: Search query
        map_type: Type of concepts to search ('all', 'chapters', 'references', 'procedures')
        
    Returns:
        Dict containing matching concept IDs and highlights
    """
    logger.info(f"Searching concepts for: {query}, type: {map_type}")
    
    # Mock search results
    matching_nodes = []
    
    if map_type in ["all", "chapters"]:
        matching_nodes.extend([
            {
                "id": f"chapter_{i}",
                "type": "chapter",
                "title": f"Chapter matching '{query}'",
                "relevance_score": 0.9 - (i * 0.1)
            }
            for i in range(3)
        ])
    
    if map_type in ["all", "references"]:
        matching_nodes.extend([
            {
                "id": f"ref_{i}",
                "type": "reference",
                "title": f"Reference about {query}",
                "relevance_score": 0.85 - (i * 0.1)
            }
            for i in range(2)
        ])
    
    return {
        "success": True,
        "data": {
            "matching_nodes": matching_nodes,
            "query": query,
            "total_matches": len(matching_nodes)
        }
    }


async def get_node_details(node_id: str) -> Dict[str, Any]:
    """
    Get detailed information about a specific node in the conceptual map
    
    Args:
        node_id: ID of the node
        
    Returns:
        Dict containing detailed node information
    """
    logger.info(f"Getting node details for: {node_id}")
    
    # Mock node details
    node_details = {
        "id": node_id,
        "type": "chapter",
        "title": "Sample Chapter Title",
        "description": "Detailed description of the chapter content...",
        "connected_nodes": [
            {"id": "ref_001", "type": "reference", "relationship": "cites"},
            {"id": "proc_001", "type": "procedure", "relationship": "discusses"},
            {"id": "chapter_002", "type": "chapter", "relationship": "related"}
        ],
        "metadata": {
            "created_at": "2024-01-15T10:30:00Z",
            "updated_at": "2024-03-20T14:45:00Z",
            "specialty": "tumor",
            "anatomical_region": "frontal",
            "completeness_score": 0.92
        }
    }
    
    return {
        "success": True,
        "data": node_details
    }


async def get_concept_clusters() -> Dict[str, Any]:
    """
    Identify and return clusters of related concepts in the knowledge graph
    
    Returns:
        Dict containing identified clusters
    """
    logger.info("Identifying concept clusters")
    
    clusters = [
        {
            "id": "cluster_1",
            "name": "Brain Tumor Management",
            "node_count": 15,
            "central_nodes": ["chapter_tumor_001", "chapter_tumor_002"],
            "specialties": ["tumor", "stereotactic"],
            "color": "#FF6B6B"
        },
        {
            "id": "cluster_2",
            "name": "Vascular Neurosurgery",
            "node_count": 12,
            "central_nodes": ["chapter_vascular_001"],
            "specialties": ["vascular"],
            "color": "#4ECDC4"
        },
        {
            "id": "cluster_3",
            "name": "Spine Surgery",
            "node_count": 18,
            "central_nodes": ["chapter_spine_001", "chapter_spine_002"],
            "specialties": ["spine"],
            "color": "#FFD93D"
        },
        {
            "id": "cluster_4",
            "name": "Functional Neurosurgery",
            "node_count": 10,
            "central_nodes": ["chapter_functional_001"],
            "specialties": ["functional", "stereotactic"],
            "color": "#95E1D3"
        }
    ]
    
    return {
        "success": True,
        "data": {
            "clusters": clusters,
            "total_clusters": len(clusters)
        }
    }


# Helper functions

def _generate_sample_chapters(specialty: Optional[str], region: Optional[str], count: int) -> List[Dict]:
    """Generate sample chapter data"""
    specialties = ["tumor", "vascular", "spine", "functional", "pediatric"]
    regions = ["frontal", "parietal", "temporal", "occipital", "cervical_spine", "lumbar_spine"]
    
    chapters = []
    for i in range(count):
        chapter_specialty = specialty or specialties[i % len(specialties)]
        chapter = {
            "id": f"chapter_{chapter_specialty}_{str(uuid.uuid4())[:8]}",
            "title": f"{chapter_specialty.capitalize()} Surgery Chapter {i+1}",
            "topic": f"Advanced {chapter_specialty} techniques",
            "specialty": chapter_specialty,
            "anatomical_region": region or regions[i % len(regions)],
            "completeness_score": 0.7 + (i % 3) * 0.1,
            "reference_count": 5 + (i % 10),
            "reference_ids": [f"ref_{str(uuid.uuid4())[:8]}" for _ in range(3)],
            "procedure_ids": [f"proc_{str(uuid.uuid4())[:8]}" for _ in range(2)]
        }
        chapters.append(chapter)
    
    return chapters


def _generate_sample_references(count: int) -> List[Dict]:
    """Generate sample reference data"""
    references = []
    evidence_levels = ["I", "II", "III", "IV"]
    
    for i in range(count):
        ref = {
            "id": f"ref_{str(uuid.uuid4())[:8]}",
            "title": f"Medical Reference {i+1}: Advanced Neurosurgical Techniques",
            "authors": [f"Author {j}" for j in range(1, 4)],
            "year": 2020 + (i % 5),
            "citation_count": 10 + (i * 5),
            "evidence_level": evidence_levels[i % len(evidence_levels)]
        }
        references.append(ref)
    
    return references


def _generate_sample_procedures(procedure_type: Optional[str], count: int) -> List[Dict]:
    """Generate sample procedure data"""
    procedure_types = ["craniotomy", "laminectomy", "fusion", "endoscopy", "stereotactic_biopsy"]
    regions = ["frontal", "cervical_spine", "lumbar_spine", "pituitary"]
    
    procedures = []
    for i in range(count):
        proc_type = procedure_type or procedure_types[i % len(procedure_types)]
        proc = {
            "id": f"proc_{proc_type}_{str(uuid.uuid4())[:8]}",
            "name": f"{proc_type.replace('_', ' ').title()} {i+1}",
            "procedure_type": proc_type,
            "anatomical_region": regions[i % len(regions)],
            "complexity": ["low", "medium", "high"][i % 3],
            "success_rate": 0.85 + (i % 3) * 0.05
        }
        procedures.append(proc)
    
    return procedures


def _get_color_for_type(node_type: str) -> str:
    """Get color for node type"""
    colors = {
        "chapter": "#3B82F6",      # Blue
        "reference": "#10B981",     # Green
        "procedure": "#F59E0B",     # Orange
        "anatomical": "#8B5CF6"     # Purple
    }
    return colors.get(node_type, "#6B7280")  # Gray default


def _are_related(chapter1: Dict, chapter2: Dict) -> bool:
    """Check if two chapters are related"""
    # Simple heuristic: same specialty or overlapping anatomical regions
    return (
        chapter1.get("specialty") == chapter2.get("specialty") or
        chapter1.get("anatomical_region") == chapter2.get("anatomical_region")
    )


def _count_by_type(items: List[Dict], key: str = "type") -> Dict[str, int]:
    """Count items by a specific key"""
    counts = defaultdict(int)
    for item in items:
        value = item.get(key)
        if value:
            counts[value] += 1
    return dict(counts)
