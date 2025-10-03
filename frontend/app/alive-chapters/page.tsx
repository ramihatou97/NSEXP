'use client'

import { useState, useEffect } from 'react'
import {
  Container,
  Typography,
  Box,
  Button,
  Paper,
  CircularProgress,
  Alert,
  Grid,
  Card,
  CardContent,
  Chip,
  Stack,
  TextField,
  LinearProgress,
} from '@mui/material'
import {
  Psychology,
  QuestionAnswer,
  CheckCircle,
  Error as ErrorIcon,
  Favorite,
  TrendingUp,
} from '@mui/icons-material'
import {
  getAliveChapterStatus,
  askChapterQuestion,
  getChapterHealth,
  getBehavioralSuggestions,
} from '@/lib/api/enhanced-services'

export default function AliveChaptersPage() {
  const [status, setStatus] = useState<any>(null)
  const [loading, setLoading] = useState(true)
  const [question, setQuestion] = useState('')
  const [chapterId, setChapterId] = useState('demo-chapter-001')
  const [questionResult, setQuestionResult] = useState<any>(null)
  const [health, setHealth] = useState<any>(null)

  useEffect(() => {
    loadStatus()
  }, [])

  const loadStatus = async () => {
    try {
      const response = await getAliveChapterStatus()
      setStatus(response)
    } catch (err) {
      console.error('Failed to load status:', err)
    } finally {
      setLoading(false)
    }
  }

  const handleAskQuestion = async () => {
    if (!question.trim()) return

    try {
      const response = await askChapterQuestion(chapterId, question)
      setQuestionResult(response)
    } catch (err: any) {
      setQuestionResult({ success: false, error: err.message })
    }
  }

  const loadHealth = async () => {
    try {
      const response = await getChapterHealth(chapterId)
      setHealth(response)
    } catch (err) {
      console.error('Failed to load health:', err)
    }
  }

  if (loading) {
    return (
      <Container sx={{ py: 4, display: 'flex', justifyContent: 'center' }}>
        <CircularProgress />
      </Container>
    )
  }

  return (
    <Container maxWidth="xl" sx={{ py: 4 }}>
      <Typography variant="h3" gutterBottom sx={{ display: 'flex', alignItems: 'center', gap: 2 }}>
        <Psychology fontSize="large" />
        Alive Chapters
      </Typography>
      <Typography variant="subtitle1" color="text.secondary" paragraph>
        Interactive, evolving chapters with Q&A, citations, and behavioral learning
      </Typography>

      <Grid container spacing={3}>
        <Grid item xs={12} md={6}>
          <Paper sx={{ p: 3, mb: 2 }}>
            <Typography variant="h6" gutterBottom>
              Feature Availability
            </Typography>
            {status && status.features && (
              <Stack spacing={2}>
                {Object.entries(status.features).map(([feature, available]) => (
                  <Box key={feature} sx={{ display: 'flex', alignItems: 'center', gap: 2 }}>
                    {available ? (
                      <CheckCircle color="success" />
                    ) : (
                      <ErrorIcon color="disabled" />
                    )}
                    <Typography>
                      {feature.replace(/_/g, ' ')}
                    </Typography>
                    <Chip
                      label={available ? 'Available' : 'Unavailable'}
                      color={available ? 'success' : 'default'}
                      size="small"
                    />
                  </Box>
                ))}
              </Stack>
            )}
            {status && (
              <Alert severity="info" sx={{ mt: 2 }}>
                Status: {status.overall_status}
              </Alert>
            )}
          </Paper>

          <Paper sx={{ p: 3 }}>
            <Typography variant="h6" gutterBottom>
              <QuestionAnswer sx={{ mr: 1 }} />
              Ask Questions
            </Typography>
            <TextField
              fullWidth
              label="Chapter ID"
              value={chapterId}
              onChange={(e) => setChapterId(e.target.value)}
              margin="normal"
              size="small"
            />
            <TextField
              fullWidth
              label="Your Question"
              value={question}
              onChange={(e) => setQuestion(e.target.value)}
              margin="normal"
              multiline
              rows={3}
              placeholder="What is the standard treatment approach?"
            />
            <Button
              variant="contained"
              onClick={handleAskQuestion}
              fullWidth
              sx={{ mt: 2 }}
              disabled={!question.trim()}
            >
              Ask Question
            </Button>

            {questionResult && (
              <Alert
                severity={questionResult.success ? 'success' : 'error'}
                sx={{ mt: 2 }}
              >
                {questionResult.success ? (
                  <Box>
                    <Typography variant="subtitle2" gutterBottom>
                      Answer:
                    </Typography>
                    <Typography variant="body2">
                      {questionResult.answer || 'Q&A engine not available'}
                    </Typography>
                    {questionResult.confidence && (
                      <Chip
                        label={`Confidence: ${(questionResult.confidence * 100).toFixed(0)}%`}
                        size="small"
                        sx={{ mt: 1 }}
                      />
                    )}
                  </Box>
                ) : (
                  questionResult.error
                )}
              </Alert>
            )}
          </Paper>
        </Grid>

        <Grid item xs={12} md={6}>
          <Paper sx={{ p: 3, mb: 2 }}>
            <Typography variant="h6" gutterBottom>
              <Favorite sx={{ mr: 1 }} />
              Chapter Health
            </Typography>
            <Button
              variant="outlined"
              onClick={loadHealth}
              fullWidth
              sx={{ mb: 2 }}
            >
              Check Chapter Health
            </Button>

            {health && health.success && health.health_metrics && (
              <Stack spacing={2}>
                <Box>
                  <Typography variant="body2" color="text.secondary">
                    Overall Health Score
                  </Typography>
                  <LinearProgress
                    variant="determinate"
                    value={health.health_metrics.overall_health_score * 100}
                    sx={{ mt: 1, height: 8, borderRadius: 1 }}
                  />
                  <Typography variant="caption">
                    {(health.health_metrics.overall_health_score * 100).toFixed(0)}%
                  </Typography>
                </Box>

                {health.health_metrics.components && (
                  <Grid container spacing={2}>
                    {Object.entries(health.health_metrics.components).map(([key, value]: [string, any]) => (
                      <Grid item xs={12} key={key}>
                        <Card variant="outlined">
                          <CardContent>
                            <Typography variant="subtitle2" gutterBottom>
                              {key.replace(/_/g, ' ')}
                            </Typography>
                            {value.score !== undefined && (
                              <Box>
                                <LinearProgress
                                  variant="determinate"
                                  value={value.score * 100}
                                  sx={{ mb: 1 }}
                                />
                                <Typography variant="caption">
                                  Score: {(value.score * 100).toFixed(0)}%
                                </Typography>
                              </Box>
                            )}
                          </CardContent>
                        </Card>
                      </Grid>
                    ))}
                  </Grid>
                )}
              </Stack>
            )}
          </Paper>

          <Paper sx={{ p: 3 }}>
            <Typography variant="h6" gutterBottom>
              <TrendingUp sx={{ mr: 1 }} />
              Behavioral Learning
            </Typography>
            <Alert severity="info">
              Behavioral learning adapts to your interaction patterns and provides
              proactive suggestions based on your usage history.
            </Alert>
          </Paper>
        </Grid>
      </Grid>
    </Container>
  )
}
