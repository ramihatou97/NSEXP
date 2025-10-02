'use client'

import { useState, useEffect, useRef } from 'react'
import {
  Container,
  Typography,
  Box,
  Paper,
  TextField,
  MenuItem,
  Card,
  CardContent,
  CircularProgress,
  Alert,
  List,
  ListItem,
  ListItemText,
  Chip,
  Divider,
  Grid,
} from '@mui/material'
import { Science, AccountTree, Link as LinkIcon } from '@mui/icons-material'
import { useChapters, useCitationNetwork } from '@/lib/hooks'

// Simple force-directed graph implementation
interface Node {
  id: string
  x: number
  y: number
  vx: number
  vy: number
  title: string
  type: string
  citationCount: number
}

interface Edge {
  source: string
  target: string
  weight: number
  type: string
}

export default function CitationsPage() {
  const [selectedChapter, setSelectedChapter] = useState('')
  const canvasRef = useRef<HTMLCanvasElement>(null)

  const { data: chapters } = useChapters({ limit: 100 })
  const { data: network, isLoading, error } = useCitationNetwork(selectedChapter || null)

  // Render network visualization
  useEffect(() => {
    if (!network || !canvasRef.current) return

    const canvas = canvasRef.current
    const ctx = canvas.getContext('2d')
    if (!ctx) return

    // Set canvas size
    const container = canvas.parentElement
    if (container) {
      canvas.width = container.clientWidth
      canvas.height = 600
    }

    // Convert network data to graph nodes/edges
    const nodes: Node[] = network.nodes.map((node, i) => ({
      id: node.id,
      x: canvas.width / 2 + Math.random() * 200 - 100,
      y: canvas.height / 2 + Math.random() * 200 - 100,
      vx: 0,
      vy: 0,
      title: node.title,
      type: node.type,
      citationCount: node.citation_count || 0,
    }))

    const edges: Edge[] = network.edges || []

    // Simple force-directed layout simulation
    const simulate = () => {
      const centerX = canvas.width / 2
      const centerY = canvas.height / 2

      // Apply forces
      nodes.forEach((node) => {
        // Center force
        const dx = centerX - node.x
        const dy = centerY - node.y
        node.vx += dx * 0.001
        node.vy += dy * 0.001

        // Repulsion between nodes
        nodes.forEach((other) => {
          if (node.id === other.id) return
          const dx = node.x - other.x
          const dy = node.y - other.y
          const dist = Math.sqrt(dx * dx + dy * dy) || 1
          const force = 100 / (dist * dist)
          node.vx += (dx / dist) * force
          node.vy += (dy / dist) * force
        })

        // Edge attraction
        edges.forEach((edge) => {
          if (edge.source === node.id) {
            const target = nodes.find((n) => n.id === edge.target)
            if (target) {
              const dx = target.x - node.x
              const dy = target.y - node.y
              node.vx += dx * 0.01
              node.vy += dy * 0.01
            }
          }
          if (edge.target === node.id) {
            const source = nodes.find((n) => n.id === edge.source)
            if (source) {
              const dx = source.x - node.x
              const dy = source.y - node.y
              node.vx += dx * 0.01
              node.vy += dy * 0.01
            }
          }
        })

        // Apply velocity with damping
        node.vx *= 0.8
        node.vy *= 0.8
        node.x += node.vx
        node.y += node.vy

        // Keep in bounds
        node.x = Math.max(30, Math.min(canvas.width - 30, node.x))
        node.y = Math.max(30, Math.min(canvas.height - 30, node.y))
      })
    }

    const render = () => {
      ctx.clearRect(0, 0, canvas.width, canvas.height)

      // Draw edges
      ctx.strokeStyle = '#ccc'
      ctx.lineWidth = 1
      edges.forEach((edge) => {
        const source = nodes.find((n) => n.id === edge.source)
        const target = nodes.find((n) => n.id === edge.target)
        if (source && target) {
          ctx.beginPath()
          ctx.moveTo(source.x, source.y)
          ctx.lineTo(target.x, target.y)
          ctx.stroke()
        }
      })

      // Draw nodes
      nodes.forEach((node) => {
        const isCenter = node.id === network.center_node
        const radius = isCenter ? 12 : 8

        // Node circle
        ctx.beginPath()
        ctx.arc(node.x, node.y, radius, 0, Math.PI * 2)
        ctx.fillStyle = isCenter ? '#1976d2' : node.type === 'chapter' ? '#43a047' : '#fb8c00'
        ctx.fill()
        ctx.strokeStyle = '#fff'
        ctx.lineWidth = 2
        ctx.stroke()

        // Node label
        ctx.fillStyle = '#333'
        ctx.font = isCenter ? 'bold 12px Arial' : '11px Arial'
        ctx.textAlign = 'center'
        ctx.textBaseline = 'top'
        const label = node.title.length > 30 ? node.title.substring(0, 27) + '...' : node.title
        ctx.fillText(label, node.x, node.y + radius + 4)
      })
    }

    // Animation loop
    let frameCount = 0
    const animate = () => {
      if (frameCount < 300) {
        simulate()
        render()
        frameCount++
        requestAnimationFrame(animate)
      } else {
        render()
      }
    }

    animate()
  }, [network])

  return (
    <Container maxWidth="xl" sx={{ py: 4 }}>
      {/* Header */}
      <Box sx={{ mb: 4 }}>
        <Typography variant="h3" gutterBottom>
          <Science sx={{ verticalAlign: 'middle', mr: 1, fontSize: 40 }} />
          Citation Network
        </Typography>
        <Typography variant="body1" color="text.secondary">
          Visualize and explore connections between chapters and references
        </Typography>
      </Box>

      {/* Chapter Selection */}
      <Paper sx={{ p: 3, mb: 3 }}>
        <TextField
          select
          fullWidth
          label="Select Chapter"
          value={selectedChapter}
          onChange={(e) => setSelectedChapter(e.target.value)}
          helperText="Choose a chapter to view its citation network"
        >
          <MenuItem value="">
            <em>Select a chapter...</em>
          </MenuItem>
          {chapters?.map((chapter) => (
            <MenuItem key={chapter.id} value={chapter.id}>
              {chapter.title}
            </MenuItem>
          ))}
        </TextField>
      </Paper>

      <Grid container spacing={3}>
        {/* Visualization */}
        <Grid item xs={12} lg={8}>
          <Paper sx={{ p: 0, overflow: 'hidden' }}>
            {!selectedChapter && (
              <Box sx={{ textAlign: 'center', py: 8 }}>
                <AccountTree sx={{ fontSize: 80, color: 'text.secondary', mb: 2 }} />
                <Typography variant="h6" color="text.secondary" gutterBottom>
                  Select a Chapter
                </Typography>
                <Typography variant="body2" color="text.secondary">
                  Choose a chapter from the dropdown above to visualize its citation network
                </Typography>
              </Box>
            )}

            {selectedChapter && isLoading && (
              <Box sx={{ textAlign: 'center', py: 8 }}>
                <CircularProgress size={60} />
                <Typography variant="body2" color="text.secondary" sx={{ mt: 2 }}>
                  Loading citation network...
                </Typography>
              </Box>
            )}

            {selectedChapter && error && (
              <Box sx={{ p: 3 }}>
                <Alert severity="error">
                  Failed to load citation network. {error.message}
                </Alert>
              </Box>
            )}

            {selectedChapter && network && !isLoading && (
              <Box>
                <canvas
                  ref={canvasRef}
                  style={{
                    width: '100%',
                    height: '600px',
                    cursor: 'grab',
                  }}
                />
              </Box>
            )}
          </Paper>
        </Grid>

        {/* Network Info */}
        <Grid item xs={12} lg={4}>
          <Card>
            <CardContent>
              <Typography variant="h6" gutterBottom>
                <LinkIcon sx={{ verticalAlign: 'middle', mr: 1 }} />
                Network Information
              </Typography>

              {network && (
                <>
                  <Box sx={{ mb: 3 }}>
                    <Typography variant="body2" color="text.secondary" gutterBottom>
                      Network Statistics
                    </Typography>
                    <Box sx={{ display: 'flex', gap: 1, flexWrap: 'wrap', mt: 1 }}>
                      <Chip
                        label={`${network.nodes.length} Nodes`}
                        size="small"
                        color="primary"
                        variant="outlined"
                      />
                      <Chip
                        label={`${network.edges.length} Connections`}
                        size="small"
                        color="secondary"
                        variant="outlined"
                      />
                    </Box>
                  </Box>

                  <Divider sx={{ my: 2 }} />

                  <Typography variant="body2" color="text.secondary" gutterBottom>
                    Legend
                  </Typography>
                  <List dense>
                    <ListItem>
                      <Box
                        sx={{
                          width: 16,
                          height: 16,
                          borderRadius: '50%',
                          bgcolor: '#1976d2',
                          mr: 2,
                        }}
                      />
                      <ListItemText primary="Center Chapter" secondary="Selected chapter" />
                    </ListItem>
                    <ListItem>
                      <Box
                        sx={{
                          width: 16,
                          height: 16,
                          borderRadius: '50%',
                          bgcolor: '#43a047',
                          mr: 2,
                        }}
                      />
                      <ListItemText primary="Related Chapters" secondary="Connected chapters" />
                    </ListItem>
                    <ListItem>
                      <Box
                        sx={{
                          width: 16,
                          height: 16,
                          borderRadius: '50%',
                          bgcolor: '#fb8c00',
                          mr: 2,
                        }}
                      />
                      <ListItemText primary="References" secondary="Cited literature" />
                    </ListItem>
                  </List>
                </>
              )}

              {!network && selectedChapter && !isLoading && (
                <Typography variant="body2" color="text.secondary">
                  No citation data available for this chapter.
                </Typography>
              )}

              {!selectedChapter && (
                <Typography variant="body2" color="text.secondary">
                  Select a chapter to view network statistics and legend.
                </Typography>
              )}
            </CardContent>
          </Card>

          {network && network.nodes.length > 0 && (
            <Card sx={{ mt: 2 }}>
              <CardContent>
                <Typography variant="h6" gutterBottom>
                  Nodes
                </Typography>
                <List dense sx={{ maxHeight: 300, overflow: 'auto' }}>
                  {network.nodes.slice(0, 10).map((node, index) => (
                    <Box key={node.id}>
                      <ListItem>
                        <ListItemText
                          primary={node.title}
                          secondary={`${node.type} • ${node.citation_count || 0} citations`}
                        />
                      </ListItem>
                      {index < Math.min(9, network.nodes.length - 1) && <Divider />}
                    </Box>
                  ))}
                  {network.nodes.length > 10 && (
                    <ListItem>
                      <ListItemText
                        secondary={`... and ${network.nodes.length - 10} more`}
                      />
                    </ListItem>
                  )}
                </List>
              </CardContent>
            </Card>
          )}
        </Grid>
      </Grid>
    </Container>
  )
}
