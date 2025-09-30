'use client'

import { useState } from 'react'
import {
  Container,
  Typography,
  Box,
  TextField,
  Button,
  MenuItem,
  Paper,
  CircularProgress,
  Alert,
} from '@mui/material'
import { AutoAwesome, Send } from '@mui/icons-material'

const specialties = [
  'Neurosurgery General',
  'Brain Tumors',
  'Vascular Neurosurgery',
  'Spine Surgery',
  'Functional Neurosurgery',
  'Pediatric Neurosurgery',
  'Trauma',
  'Skull Base',
]

export default function SynthesisPage() {
  const [topic, setTopic] = useState('')
  const [specialty, setSpecialty] = useState('Neurosurgery General')
  const [loading, setLoading] = useState(false)
  const [error, setError] = useState('')

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault()
    setLoading(true)
    setError('')

    try {
      const response = await fetch('http://localhost:8000/api/v1/synthesis/generate', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          topic,
          specialty: specialty.toLowerCase().replace(/ /g, '_'),
          max_sources: 15,
        }),
      })

      const data = await response.json()
      
      if (data.success) {
        alert('Synthesis started! Check back in a few moments.')
      } else {
        setError(data.error || 'Synthesis failed')
      }
    } catch (err) {
      setError('Failed to connect to backend. Make sure the backend is running on http://localhost:8000')
    } finally {
      setLoading(false)
    }
  }

  return (
    <Container maxWidth="md" sx={{ py: 4 }}>
      <Box sx={{ mb: 4 }}>
        <Typography variant="h3" gutterBottom>
          <AutoAwesome sx={{ verticalAlign: 'middle', mr: 1, fontSize: 40 }} />
          AI Synthesis
        </Typography>
        <Typography variant="body1" color="text.secondary">
          Generate comprehensive neurosurgical chapters using AI
        </Typography>
      </Box>

      <Paper sx={{ p: 4 }}>
        <form onSubmit={handleSubmit}>
          <TextField
            fullWidth
            label="Topic"
            placeholder="e.g., Glioblastoma Management, Aneurysm Clipping, Spinal Fusion"
            value={topic}
            onChange={(e) => setTopic(e.target.value)}
            required
            sx={{ mb: 3 }}
          />

          <TextField
            fullWidth
            select
            label="Specialty"
            value={specialty}
            onChange={(e) => setSpecialty(e.target.value)}
            sx={{ mb: 3 }}
          >
            {specialties.map((option) => (
              <MenuItem key={option} value={option}>
                {option}
              </MenuItem>
            ))}
          </TextField>

          {error && (
            <Alert severity="error" sx={{ mb: 3 }}>
              {error}
            </Alert>
          )}

          <Button
            type="submit"
            variant="contained"
            size="large"
            fullWidth
            disabled={loading || !topic}
            startIcon={loading ? <CircularProgress size={20} /> : <Send />}
          >
            {loading ? 'Generating...' : 'Generate Chapter'}
          </Button>
        </form>
      </Paper>

      <Box sx={{ mt: 3, p: 2, bgcolor: 'info.light', borderRadius: 2 }}>
        <Typography variant="body2">
          💡 <strong>Tip:</strong> Be specific with your topic for better results. The AI will synthesize content from multiple medical sources and create a comprehensive chapter.
        </Typography>
      </Box>
    </Container>
  )
}
