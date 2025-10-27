'use client'

import { useState, useEffect, useCallback, useRef } from 'react'
import {
  Container,
  Typography,
  Box,
  Paper,
  TextField,
  MenuItem,
  Button,
  Card,
  CardContent,
  CircularProgress,
  Alert,
  Grid,
  Chip,
  FormControlLabel,
  Switch,
  IconButton,
  Tooltip,
  Divider,
  List,
  ListItem,
  ListItemText,
} from '@mui/material'
import {
  AccountTree,
  Search as SearchIcon,
  ZoomIn,
  ZoomOut,
  CenterFocusStrong,
  FilterList,
  Info,
  GetApp,
} from '@mui/icons-material'
import ForceGraph2D from 'react-force-graph-2d'
import axios from 'axios'

// Type definitions
interface Node {
  id: string
  label: string
  type: string
  specialty?: string
  anatomical_region?: string
  procedure_type?: string
  year?: number
  size: number
  color: string
  metadata?: any
}

interface Edge {
  source: string
  target: string
  type: string
  weight: number
  label: string
}

interface ConceptualMapData {
  nodes: Node[]
  edges: Edge[]
  statistics: {
    total_nodes: number
    total_edges: number
    node_types: Record<string, number>
    edge_types: Record<string, number>
    specialties: Record<string, number>
    anatomical_regions: Record<string, number>
  }
  filters_applied: {
    specialty?: string
    anatomical_region?: string
    procedure_type?: string
  }
}

export default function ConceptualMapPage() {
  const [mapData, setMapData] = useState<ConceptualMapData | null>(null)
  const [loading, setLoading] = useState(false)
  const [error, setError] = useState<string | null>(null)
  const [searchQuery, setSearchQuery] = useState('')
  const [highlightedNodes, setHighlightedNodes] = useState<Set<string>>(new Set())
  
  // Filters
  const [specialty, setSpecialty] = useState<string>('')
  const [anatomicalRegion, setAnatomicalRegion] = useState<string>('')
  const [procedureType, setProcedureType] = useState<string>('')
  const [includeReferences, setIncludeReferences] = useState(true)
  const [includeProcedures, setIncludeProcedures] = useState(true)
  const [maxNodes, setMaxNodes] = useState(100)
  
  // Graph state
  const graphRef = useRef<any>()
  const [selectedNode, setSelectedNode] = useState<Node | null>(null)
  const [hoveredNode, setHoveredNode] = useState<Node | null>(null)

  const specialties = [
    { value: '', label: 'All Specialties' },
    { value: 'tumor', label: 'Tumor' },
    { value: 'vascular', label: 'Vascular' },
    { value: 'spine', label: 'Spine' },
    { value: 'functional', label: 'Functional' },
    { value: 'pediatric', label: 'Pediatric' },
    { value: 'trauma', label: 'Trauma' },
  ]

  const anatomicalRegions = [
    { value: '', label: 'All Regions' },
    { value: 'frontal', label: 'Frontal' },
    { value: 'parietal', label: 'Parietal' },
    { value: 'temporal', label: 'Temporal' },
    { value: 'occipital', label: 'Occipital' },
    { value: 'cerebellum', label: 'Cerebellum' },
    { value: 'cervical_spine', label: 'Cervical Spine' },
    { value: 'lumbar_spine', label: 'Lumbar Spine' },
  ]

  const procedureTypes = [
    { value: '', label: 'All Procedures' },
    { value: 'craniotomy', label: 'Craniotomy' },
    { value: 'laminectomy', label: 'Laminectomy' },
    { value: 'fusion', label: 'Fusion' },
    { value: 'endoscopy', label: 'Endoscopy' },
    { value: 'stereotactic_biopsy', label: 'Stereotactic Biopsy' },
  ]

  // Fetch conceptual map data
  const fetchConceptualMap = useCallback(async () => {
    setLoading(true)
    setError(null)
    try {
      const params: any = {
        include_references: includeReferences,
        include_procedures: includeProcedures,
        max_nodes: maxNodes,
      }
      
      if (specialty) params.specialty = specialty
      if (anatomicalRegion) params.anatomical_region = anatomicalRegion
      if (procedureType) params.procedure_type = procedureType

      const response = await axios.get('http://localhost:8000/api/v1/conceptual-map', { params })
      
      if (response.data.success) {
        setMapData(response.data.data)
      } else {
        setError('Failed to load conceptual map')
      }
    } catch (err: any) {
      setError(err.response?.data?.message || 'Failed to load conceptual map')
      console.error('Error fetching conceptual map:', err)
    } finally {
      setLoading(false)
    }
  }, [specialty, anatomicalRegion, procedureType, includeReferences, includeProcedures, maxNodes])

  // Search concepts
  const handleSearch = async () => {
    if (!searchQuery.trim()) {
      setHighlightedNodes(new Set())
      return
    }

    try {
      const response = await axios.get('http://localhost:8000/api/v1/conceptual-map/search', {
        params: { query: searchQuery, map_type: 'all' }
      })
      
      if (response.data.success) {
        const matchingIds = new Set(
          response.data.data.matching_nodes.map((node: any) => node.id)
        )
        setHighlightedNodes(matchingIds)
      }
    } catch (err) {
      console.error('Search error:', err)
    }
  }

  // Load data on mount and when filters change
  useEffect(() => {
    fetchConceptualMap()
  }, [fetchConceptualMap])

  // Handle node click
  const handleNodeClick = useCallback((node: any) => {
    setSelectedNode(node)
  }, [])

  // Handle node hover
  const handleNodeHover = useCallback((node: any) => {
    setHoveredNode(node)
  }, [])

  // Graph controls
  const handleZoomIn = () => {
    if (graphRef.current) {
      graphRef.current.zoom(1.5, 400)
    }
  }

  const handleZoomOut = () => {
    if (graphRef.current) {
      graphRef.current.zoom(0.67, 400)
    }
  }

  const handleCenter = () => {
    if (graphRef.current) {
      graphRef.current.zoomToFit(400, 50)
    }
  }

  // Export data
  const handleExport = () => {
    if (!mapData) return
    
    const dataStr = JSON.stringify(mapData, null, 2)
    const dataBlob = new Blob([dataStr], { type: 'application/json' })
    const url = URL.createObjectURL(dataBlob)
    const link = document.createElement('a')
    link.href = url
    link.download = 'conceptual-map.json'
    link.click()
    URL.revokeObjectURL(url)
  }

  return (
    <Container maxWidth="xl" sx={{ py: 4 }}>
      {/* Header */}
      <Box sx={{ mb: 4 }}>
        <Box sx={{ display: 'flex', alignItems: 'center', mb: 2 }}>
          <AccountTree sx={{ fontSize: 40, mr: 2, color: 'primary.main' }} />
          <Typography variant="h4" component="h1">
            Conceptual Knowledge Map
          </Typography>
        </Box>
        <Typography variant="body1" color="text.secondary">
          Interactive visualization of neurosurgical knowledge relationships across chapters, references, procedures, and anatomical regions
        </Typography>
      </Box>

      {/* Filters */}
      <Paper sx={{ p: 3, mb: 3 }}>
        <Box sx={{ display: 'flex', alignItems: 'center', mb: 2 }}>
          <FilterList sx={{ mr: 1 }} />
          <Typography variant="h6">Filters</Typography>
        </Box>
        
        <Grid container spacing={2}>
          <Grid item xs={12} md={3}>
            <TextField
              select
              fullWidth
              label="Specialty"
              value={specialty}
              onChange={(e) => setSpecialty(e.target.value)}
              size="small"
            >
              {specialties.map((option) => (
                <MenuItem key={option.value} value={option.value}>
                  {option.label}
                </MenuItem>
              ))}
            </TextField>
          </Grid>
          
          <Grid item xs={12} md={3}>
            <TextField
              select
              fullWidth
              label="Anatomical Region"
              value={anatomicalRegion}
              onChange={(e) => setAnatomicalRegion(e.target.value)}
              size="small"
            >
              {anatomicalRegions.map((option) => (
                <MenuItem key={option.value} value={option.value}>
                  {option.label}
                </MenuItem>
              ))}
            </TextField>
          </Grid>
          
          <Grid item xs={12} md={3}>
            <TextField
              select
              fullWidth
              label="Procedure Type"
              value={procedureType}
              onChange={(e) => setProcedureType(e.target.value)}
              size="small"
            >
              {procedureTypes.map((option) => (
                <MenuItem key={option.value} value={option.value}>
                  {option.label}
                </MenuItem>
              ))}
            </TextField>
          </Grid>
          
          <Grid item xs={12} md={3}>
            <TextField
              fullWidth
              type="number"
              label="Max Nodes"
              value={maxNodes}
              onChange={(e) => setMaxNodes(parseInt(e.target.value) || 100)}
              size="small"
              inputProps={{ min: 10, max: 500 }}
            />
          </Grid>
          
          <Grid item xs={12} md={6}>
            <FormControlLabel
              control={
                <Switch
                  checked={includeReferences}
                  onChange={(e) => setIncludeReferences(e.target.checked)}
                />
              }
              label="Include References"
            />
            <FormControlLabel
              control={
                <Switch
                  checked={includeProcedures}
                  onChange={(e) => setIncludeProcedures(e.target.checked)}
                />
              }
              label="Include Procedures"
            />
          </Grid>
          
          <Grid item xs={12} md={6}>
            <Box sx={{ display: 'flex', gap: 1, justifyContent: 'flex-end' }}>
              <Button
                variant="outlined"
                onClick={() => {
                  setSpecialty('')
                  setAnatomicalRegion('')
                  setProcedureType('')
                  setMaxNodes(100)
                  setIncludeReferences(true)
                  setIncludeProcedures(true)
                }}
              >
                Reset Filters
              </Button>
              <Button
                variant="contained"
                onClick={fetchConceptualMap}
                disabled={loading}
              >
                Apply Filters
              </Button>
            </Box>
          </Grid>
        </Grid>
      </Paper>

      {/* Search */}
      <Paper sx={{ p: 2, mb: 3 }}>
        <Box sx={{ display: 'flex', gap: 1 }}>
          <TextField
            fullWidth
            placeholder="Search concepts..."
            value={searchQuery}
            onChange={(e) => setSearchQuery(e.target.value)}
            onKeyPress={(e) => e.key === 'Enter' && handleSearch()}
            size="small"
            InputProps={{
              startAdornment: <SearchIcon sx={{ mr: 1, color: 'text.secondary' }} />
            }}
          />
          <Button variant="contained" onClick={handleSearch}>
            Search
          </Button>
        </Box>
      </Paper>

      {error && (
        <Alert severity="error" sx={{ mb: 3 }} onClose={() => setError(null)}>
          {error}
        </Alert>
      )}

      {/* Main Content */}
      <Grid container spacing={3}>
        {/* Graph Visualization */}
        <Grid item xs={12} md={9}>
          <Paper sx={{ position: 'relative', height: 700 }}>
            {loading && (
              <Box sx={{ display: 'flex', justifyContent: 'center', alignItems: 'center', height: '100%' }}>
                <CircularProgress />
              </Box>
            )}
            
            {!loading && mapData && (
              <>
                {/* Graph Controls */}
                <Box sx={{ position: 'absolute', top: 16, right: 16, zIndex: 10, display: 'flex', gap: 1 }}>
                  <Tooltip title="Zoom In">
                    <IconButton onClick={handleZoomIn} sx={{ bgcolor: 'background.paper' }}>
                      <ZoomIn />
                    </IconButton>
                  </Tooltip>
                  <Tooltip title="Zoom Out">
                    <IconButton onClick={handleZoomOut} sx={{ bgcolor: 'background.paper' }}>
                      <ZoomOut />
                    </IconButton>
                  </Tooltip>
                  <Tooltip title="Center View">
                    <IconButton onClick={handleCenter} sx={{ bgcolor: 'background.paper' }}>
                      <CenterFocusStrong />
                    </IconButton>
                  </Tooltip>
                  <Tooltip title="Export Data">
                    <IconButton onClick={handleExport} sx={{ bgcolor: 'background.paper' }}>
                      <GetApp />
                    </IconButton>
                  </Tooltip>
                </Box>

                {/* Force Graph */}
                <ForceGraph2D
                  ref={graphRef}
                  graphData={{
                    nodes: mapData.nodes,
                    links: mapData.edges.map(edge => ({
                      source: edge.source,
                      target: edge.target,
                      ...edge
                    }))
                  }}
                  width={undefined}
                  height={700}
                  nodeId="id"
                  nodeLabel="label"
                  nodeColor={(node: any) => 
                    highlightedNodes.has(node.id) ? '#FF6B6B' : node.color
                  }
                  nodeRelSize={6}
                  nodeVal={(node: any) => node.size}
                  linkColor={() => '#999'}
                  linkWidth={(link: any) => link.weight * 2}
                  linkDirectionalParticles={2}
                  linkDirectionalParticleWidth={(link: any) => link.weight * 2}
                  onNodeClick={handleNodeClick}
                  onNodeHover={handleNodeHover}
                  enableNodeDrag={true}
                  cooldownTime={3000}
                  d3AlphaDecay={0.02}
                  d3VelocityDecay={0.3}
                />
              </>
            )}
          </Paper>
        </Grid>

        {/* Sidebar */}
        <Grid item xs={12} md={3}>
          {/* Legend */}
          <Card sx={{ mb: 2 }}>
            <CardContent>
              <Typography variant="h6" gutterBottom sx={{ display: 'flex', alignItems: 'center' }}>
                <Info sx={{ mr: 1, fontSize: 20 }} />
                Legend
              </Typography>
              <Divider sx={{ mb: 2 }} />
              <Box sx={{ display: 'flex', flexDirection: 'column', gap: 1 }}>
                <Box sx={{ display: 'flex', alignItems: 'center', gap: 1 }}>
                  <Box sx={{ width: 16, height: 16, borderRadius: '50%', bgcolor: '#3B82F6' }} />
                  <Typography variant="body2">Chapters</Typography>
                </Box>
                <Box sx={{ display: 'flex', alignItems: 'center', gap: 1 }}>
                  <Box sx={{ width: 16, height: 16, borderRadius: '50%', bgcolor: '#10B981' }} />
                  <Typography variant="body2">References</Typography>
                </Box>
                <Box sx={{ display: 'flex', alignItems: 'center', gap: 1 }}>
                  <Box sx={{ width: 16, height: 16, borderRadius: '50%', bgcolor: '#F59E0B' }} />
                  <Typography variant="body2">Procedures</Typography>
                </Box>
              </Box>
            </CardContent>
          </Card>

          {/* Statistics */}
          {mapData && (
            <Card sx={{ mb: 2 }}>
              <CardContent>
                <Typography variant="h6" gutterBottom>
                  Statistics
                </Typography>
                <Divider sx={{ mb: 2 }} />
                <Box sx={{ display: 'flex', flexDirection: 'column', gap: 1 }}>
                  <Typography variant="body2">
                    <strong>Total Nodes:</strong> {mapData.statistics.total_nodes}
                  </Typography>
                  <Typography variant="body2">
                    <strong>Total Edges:</strong> {mapData.statistics.total_edges}
                  </Typography>
                  <Typography variant="body2" sx={{ mt: 1 }}>
                    <strong>Node Types:</strong>
                  </Typography>
                  {Object.entries(mapData.statistics.node_types).map(([type, count]) => (
                    <Typography key={type} variant="body2" sx={{ pl: 2 }}>
                      {type}: {count}
                    </Typography>
                  ))}
                </Box>
              </CardContent>
            </Card>
          )}

          {/* Selected Node Details */}
          {selectedNode && (
            <Card>
              <CardContent>
                <Typography variant="h6" gutterBottom>
                  Selected Node
                </Typography>
                <Divider sx={{ mb: 2 }} />
                <Typography variant="subtitle2" gutterBottom>
                  {selectedNode.label}
                </Typography>
                <Chip
                  label={selectedNode.type}
                  size="small"
                  sx={{ mb: 2 }}
                />
                {selectedNode.specialty && (
                  <Typography variant="body2">
                    <strong>Specialty:</strong> {selectedNode.specialty}
                  </Typography>
                )}
                {selectedNode.anatomical_region && (
                  <Typography variant="body2">
                    <strong>Region:</strong> {selectedNode.anatomical_region}
                  </Typography>
                )}
                {selectedNode.metadata && selectedNode.metadata.completeness_score && (
                  <Typography variant="body2">
                    <strong>Completeness:</strong> {(selectedNode.metadata.completeness_score * 100).toFixed(0)}%
                  </Typography>
                )}
              </CardContent>
            </Card>
          )}
        </Grid>
      </Grid>
    </Container>
  )
}
