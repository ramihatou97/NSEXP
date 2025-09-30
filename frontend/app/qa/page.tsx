'use client'

import { useState } from 'react'
import {
  Container,
  Typography,
  Box,
  TextField,
  Button,
  Paper,
  CircularProgress,
  Alert,
} from '@mui/material'
import { Psychology, Send } from '@mui/icons-material'

export default function QAPage() {
  const [question, setQuestion] = useState('')
  const [answer, setAnswer] = useState('')
  const [loading, setLoading] = useState(false)
  const [error, setError] = useState('')

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault()
    setLoading(true)
    setError('')
    setAnswer('')

    try {
      const response = await fetch('http://localhost:8000/api/v1/qa/ask', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ question }),
      })

      const data = await response.json()
      
      if (data.success) {
        setAnswer(data.data.answer)
      } else {
        setError(data.error || 'Failed to get answer')
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
          <Psychology sx={{ verticalAlign: 'middle', mr: 1, fontSize: 40 }} />
          Q&A Assistant
        </Typography>
        <Typography variant="body1" color="text.secondary">
          Ask neurosurgical questions and get AI-powered answers
        </Typography>
      </Box>

      <Paper sx={{ p: 4, mb: 3 }}>
        <form onSubmit={handleSubmit}>
          <TextField
            fullWidth
            multiline
            rows={4}
            label="Your Question"
            placeholder="e.g., What are the indications for craniotomy in glioblastoma?"
            value={question}
            onChange={(e) => setQuestion(e.target.value)}
            required
            sx={{ mb: 3 }}
          />

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
            disabled={loading || !question}
            startIcon={loading ? <CircularProgress size={20} /> : <Send />}
          >
            {loading ? 'Asking...' : 'Ask Question'}
          </Button>
        </form>
      </Paper>

      {answer && (
        <Paper sx={{ p: 4, bgcolor: 'grey.50' }}>
          <Typography variant="h6" gutterBottom>
            Answer:
          </Typography>
          <Typography variant="body1" sx={{ whiteSpace: 'pre-wrap' }}>
            {answer}
          </Typography>
        </Paper>
      )}
    </Container>
  )
}
