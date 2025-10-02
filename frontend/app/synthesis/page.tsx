'use client'

import { useState } from 'react'
import { useRouter } from 'next/navigation'
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
  LinearProgress,
  Stepper,
  Step,
  StepLabel,
  Card,
  CardContent,
  Chip,
} from '@mui/material'
import {
  AutoAwesome,
  Send,
  CheckCircle,
  Error as ErrorIcon,
  WifiOff,
} from '@mui/icons-material'
import { useSynthesisWithProgress } from '@/lib/hooks/useWebSocket'

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

const synthesisSteps = [
  'Searching Medical Literature',
  'Analyzing Sources',
  'Synthesizing Content',
  'Generating Chapter',
]

export default function SynthesisPage() {
  const router = useRouter()
  const [topic, setTopic] = useState('')
  const [specialty, setSpecialty] = useState('Neurosurgery General')

  const {
    startSynthesis,
    reset,
    isGenerating,
    progress,
    result,
    error,
    isConnected,
  } = useSynthesisWithProgress()

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault()
    await startSynthesis(
      topic,
      specialty.toLowerCase().replace(/ /g, '_'),
      15
    )
  }

  const handleViewChapter = () => {
    if (result?.chapter_id) {
      router.push(`/library/${result.chapter_id}`)
    }
  }

  const handleReset = () => {
    reset()
    setTopic('')
  }

  // Calculate active step based on progress status
  const getActiveStep = () => {
    if (!progress) return -1
    switch (progress.status) {
      case 'searching':
        return 0
      case 'analyzing':
        return 1
      case 'synthesizing':
        return 2
      case 'generating':
        return 3
      case 'completed':
        return 4
      case 'failed':
        return -1
      default:
        return -1
    }
  }

  return (
    <Container maxWidth="md" sx={{ py: 4 }}>
      {/* Header */}
      <Box sx={{ mb: 4 }}>
        <Typography variant="h3" gutterBottom>
          <AutoAwesome sx={{ verticalAlign: 'middle', mr: 1, fontSize: 40 }} />
          AI Synthesis
        </Typography>
        <Typography variant="body1" color="text.secondary">
          Generate comprehensive neurosurgical chapters using AI
        </Typography>
      </Box>

      {/* WebSocket Status */}
      {!isConnected && (
        <Alert severity="warning" icon={<WifiOff />} sx={{ mb: 3 }}>
          Real-time updates unavailable. Progress will not be displayed live.
        </Alert>
      )}

      {/* Synthesis Form (shown when not generating) */}
      {!isGenerating && !result && (
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
                {error.message || 'Synthesis failed. Please try again.'}
              </Alert>
            )}

            <Button
              type="submit"
              variant="contained"
              size="large"
              fullWidth
              disabled={!topic}
              startIcon={<Send />}
            >
              Generate Chapter
            </Button>
          </form>
        </Paper>
      )}

      {/* Progress Display (shown during generation) */}
      {isGenerating && (
        <Paper sx={{ p: 4 }}>
          <Box sx={{ mb: 3 }}>
            <Box sx={{ display: 'flex', alignItems: 'center', mb: 2 }}>
              <CircularProgress size={24} sx={{ mr: 2 }} />
              <Typography variant="h6">
                Generating: {topic}
              </Typography>
            </Box>

            {progress && (
              <>
                <Typography variant="body2" color="text.secondary" gutterBottom>
                  {progress.message}
                </Typography>

                {/* Progress Bar */}
                <Box sx={{ mt: 2, mb: 4 }}>
                  <LinearProgress
                    variant="determinate"
                    value={progress.progress}
                    sx={{ height: 8, borderRadius: 4 }}
                  />
                  <Box sx={{ display: 'flex', justifyContent: 'space-between', mt: 1 }}>
                    <Typography variant="caption" color="text.secondary">
                      {progress.current_step}
                    </Typography>
                    <Typography variant="caption" color="text.secondary">
                      {progress.progress}%
                    </Typography>
                  </Box>
                </Box>

                {/* Synthesis Steps */}
                <Stepper activeStep={getActiveStep()} sx={{ mt: 3 }}>
                  {synthesisSteps.map((label, index) => (
                    <Step key={label}>
                      <StepLabel>{label}</StepLabel>
                    </Step>
                  ))}
                </Stepper>
              </>
            )}

            {!progress && (
              <Box sx={{ textAlign: 'center', py: 2 }}>
                <Typography variant="body2" color="text.secondary">
                  Initializing synthesis...
                </Typography>
              </Box>
            )}
          </Box>
        </Paper>
      )}

      {/* Success Result (shown after completion) */}
      {result && !error && (
        <Card>
          <CardContent>
            <Box sx={{ textAlign: 'center', py: 3 }}>
              <CheckCircle color="success" sx={{ fontSize: 64, mb: 2 }} />
              <Typography variant="h5" gutterBottom>
                Synthesis Complete!
              </Typography>
              <Typography variant="body2" color="text.secondary" paragraph>
                Your chapter has been successfully generated and saved to the library.
              </Typography>

              {progress && (
                <Box sx={{ display: 'flex', gap: 1, justifyContent: 'center', mb: 3 }}>
                  {progress.completed_steps && progress.total_steps && (
                    <Chip
                      label={`${progress.completed_steps}/${progress.total_steps} steps completed`}
                      size="small"
                      color="primary"
                    />
                  )}
                </Box>
              )}

              <Box sx={{ display: 'flex', gap: 2, justifyContent: 'center', mt: 3 }}>
                <Button
                  variant="contained"
                  onClick={handleViewChapter}
                  startIcon={<AutoAwesome />}
                >
                  View Chapter
                </Button>
                <Button variant="outlined" onClick={handleReset}>
                  Generate Another
                </Button>
              </Box>
            </Box>
          </CardContent>
        </Card>
      )}

      {/* Error Result */}
      {error && !isGenerating && (
        <Card>
          <CardContent>
            <Box sx={{ textAlign: 'center', py: 3 }}>
              <ErrorIcon color="error" sx={{ fontSize: 64, mb: 2 }} />
              <Typography variant="h5" gutterBottom>
                Synthesis Failed
              </Typography>
              <Typography variant="body2" color="text.secondary" paragraph>
                {error.message || 'An error occurred during synthesis. Please try again.'}
              </Typography>

              <Button variant="contained" onClick={handleReset} sx={{ mt: 2 }}>
                Try Again
              </Button>
            </Box>
          </CardContent>
        </Card>
      )}

      {/* Tips Section */}
      {!isGenerating && !result && (
        <Box sx={{ mt: 3, p: 2, bgcolor: 'info.light', borderRadius: 2 }}>
          <Typography variant="body2">
            💡 <strong>Tip:</strong> Be specific with your topic for better results. The AI will
            synthesize content from multiple medical sources and create a comprehensive chapter.
          </Typography>
          {isConnected && (
            <Typography variant="body2" sx={{ mt: 1 }}>
              ⚡ <strong>Real-time updates enabled:</strong> You'll see live progress as your
              chapter is being generated.
            </Typography>
          )}
        </Box>
      )}
    </Container>
  )
}
