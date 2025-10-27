# Conceptual Knowledge Map Feature

## Overview

The Conceptual Knowledge Map is an interactive visualization feature that displays relationships between chapters, references, procedures, and anatomical regions in the neurosurgical knowledge base.

## Features

### Interactive Visualization
- **Force-directed graph**: Nodes represent concepts (chapters, references, procedures)
- **Edges**: Show relationships (citations, references, related topics)
- **Interactive controls**: Zoom, pan, drag nodes
- **Color-coded nodes**: Blue (chapters), Green (references), Orange (procedures)

### Filtering Options
- **Specialty**: Filter by neurosurgical specialty (tumor, vascular, spine, etc.)
- **Anatomical Region**: Filter by brain/spine region (frontal, temporal, cervical, etc.)
- **Procedure Type**: Filter by surgical procedure (craniotomy, laminectomy, etc.)
- **Node Types**: Toggle inclusion of references and procedures
- **Max Nodes**: Control graph complexity (10-500 nodes)

### Search & Navigation
- **Concept Search**: Find and highlight specific concepts
- **Node Selection**: Click nodes to view detailed information
- **Export**: Download graph data as JSON

### Statistics
- View total node and edge counts
- See distribution by type, specialty, and region
- Identify concept clusters

## Usage

### Accessing the Map
1. Navigate to the "Concept Map" link in the main navigation
2. The map will load with default settings (100 nodes)

### Filtering the Map
1. Use the filter panel at the top
2. Select specialty, region, or procedure type
3. Click "Apply Filters" to update the visualization
4. Click "Reset Filters" to clear all filters

### Searching Concepts
1. Enter a search term in the search box
2. Press Enter or click "Search"
3. Matching nodes will be highlighted in red

### Interacting with Nodes
1. **Click** a node to select it and view details in the sidebar
2. **Hover** over nodes to see tooltips
3. **Drag** nodes to rearrange the graph
4. Use **zoom controls** (top right) to zoom in/out or center the view

### Exporting Data
1. Click the download icon (top right)
2. Graph data will be exported as `conceptual-map.json`

## API Endpoints

### Get Conceptual Map
```
GET /api/v1/conceptual-map
```

Query Parameters:
- `specialty` (optional): Filter by specialty
- `anatomical_region` (optional): Filter by region
- `procedure_type` (optional): Filter by procedure
- `include_references` (boolean, default: true): Include reference nodes
- `include_procedures` (boolean, default: true): Include procedure nodes
- `max_nodes` (integer, default: 100): Maximum nodes to return

Response:
```json
{
  "success": true,
  "data": {
    "nodes": [...],
    "edges": [...],
    "statistics": {...},
    "filters_applied": {...}
  }
}
```

### Search Concepts
```
GET /api/v1/conceptual-map/search?query=tumor&map_type=all
```

### Get Node Details
```
GET /api/v1/conceptual-map/node/{node_id}
```

### Get Concept Clusters
```
GET /api/v1/conceptual-map/clusters
```

## Technical Details

### Frontend
- **Component**: `/frontend/app/conceptual-map/page.tsx`
- **Library**: `react-force-graph-2d` for visualization
- **State Management**: React hooks (useState, useEffect, useCallback)
- **Styling**: Material-UI components with custom theming

### Backend
- **Service**: `/backend/services/conceptual_map_service.py`
- **Endpoints**: 4 endpoints in `main_simplified.py`
- **Data Generation**: Mock data with realistic relationships
- **Async Support**: Full async/await pattern

### Data Structure

**Node Object**:
```python
{
  "id": str,              # Unique identifier
  "label": str,           # Display name
  "type": str,            # "chapter", "reference", "procedure"
  "specialty": str,       # Neurosurgical specialty
  "size": int,            # Visual size
  "color": str,           # Hex color code
  "metadata": dict        # Additional properties
}
```

**Edge Object**:
```python
{
  "source": str,          # Source node ID
  "target": str,          # Target node ID
  "type": str,            # "cites", "discusses", "related"
  "weight": float,        # Relationship strength
  "label": str            # Display label
}
```

## Use Cases

### For Residents
- Explore relationships between surgical procedures and anatomical regions
- Understand citation patterns in neurosurgical literature
- Discover related topics for comprehensive learning

### For Researchers
- Identify knowledge gaps and under-connected concepts
- Find relevant references for specific procedures
- Visualize citation networks and research trends

### For Educators
- Create visual learning materials
- Show interconnections between topics
- Demonstrate evidence-based practice patterns

## Future Enhancements

Potential improvements:
- [ ] Real database integration (currently uses mock data)
- [ ] 3D visualization option
- [ ] Time-based filtering (show knowledge evolution)
- [ ] Community detection algorithms for better clustering
- [ ] Path finding between concepts
- [ ] Save and share custom views
- [ ] Integration with chapter editing workflow
- [ ] Collaborative annotation features

## Troubleshooting

### Graph Not Loading
- Check browser console for errors
- Verify backend is running on port 8000
- Check CORS settings if accessing from different origin

### Performance Issues
- Reduce `max_nodes` parameter (try 50)
- Disable references or procedures
- Clear browser cache

### Visualization Issues
- Try zooming out (use zoom controls)
- Click "Center View" to reset position
- Refresh the page to reload data

## Related Features

- **Citations Network**: `/citations` - Chapter-specific citation visualization
- **Library**: `/library` - Browse and manage chapters
- **Search**: `/search` - Full-text content search
- **Procedures**: `/procedures` - Surgical procedure database
