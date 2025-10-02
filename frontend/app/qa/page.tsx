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
  Card,
  CardContent,
  Divider,
  Chip,
  IconButton,
  Collapse,
  MenuItem,
} from '@mui/material'
import {
  Psychology,
  Send,
  History,
  ExpandMore,
  ExpandLess,
  AccessTime,
  FilterList,
} from '@mui/icons-material'
import { useQAQuestion, useQAHistory, useChapters } from '@/lib/hooks'

export default function QAPage() {
  const [question, setQuestion] = useState('')
  const [context, setContext] = useState('')
  const [showHistory, setShowHistory] = useState(true)
  const [selectedChapter, setSelectedChapter] = useState('')

  const askQuestion = useQAQuestion()
  const { data: history, isLoading: historyLoading } = useQAHistory({
    chapter_id: selectedChapter || undefined,
    limit: 20,
  })
  const { data: chapters } = useChapters({ limit: 100 })

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault()
    if (!question.trim()) return

    await askQuestion.mutateAsync({
      question,
      chapter_id: selectedChapter || undefined,
      context: context.trim() || undefined,
    })
    setQuestion('')
    setContext('')
  }

  return (
    <Container maxWidth="lg" sx={{ py: 4 }}>
      {/* Header */}
      <Box sx={{ mb: 4 }}>
        <Typography variant="h3" gutterBottom>
          <Psychology sx={{ verticalAlign: 'middle', mr: 1, fontSize: 40 }} />
          Q&A Assistant
        </Typography>
        <Typography variant="body1" color="text.secondary">
          Ask neurosurgical questions and get AI-powered answers
        </Typography>
      </Box>

      <Box sx={{ display: 'flex', gap: 3, flexDirection: { xs: 'column', md: 'row' } }}>
        {/* Question Input */}
        <Box sx={{ flex: 1 }}>
          <Paper sx={{ p: 4, mb: 3 }}>
            <form onSubmit={handleSubmit}>
              <TextField
                select
                fullWidth
                label="Chapter Context (Optional)"
                value={selectedChapter}
                onChange={(e) => setSelectedChapter(e.target.value)}
                helperText="Select a chapter to ask questions specific to that content"
                sx={{ mb: 3 }}
              >
                <MenuItem value="">
                  <em>All Chapters</em>
                </MenuItem>
                {chapters?.map((chapter) => (
                  <MenuItem key={chapter.id} value={chapter.id}>
                    {chapter.title}
                  </MenuItem>
                ))}
              </TextField>

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

              <TextField
                fullWidth
                multiline
                rows={3}
                label="Additional Context (Optional)"
                placeholder="e.g., Patient is 45 years old with left temporal lobe involvement..."
                value={context}
                onChange={(e) => setContext(e.target.value)}
                helperText="Provide additional context to get more relevant answers"
                sx={{ mb: 3 }}
              />

              {askQuestion.error && (
                <Alert severity="error" sx={{ mb: 3 }}>
                  {askQuestion.error instanceof Error
                    ? askQuestion.error.message
                    : 'Failed to get answer'}
                </Alert>
              )}

              <Button
                type="submit"
                variant="contained"
                size="large"
                fullWidth
                disabled={askQuestion.isPending || !question.trim()}
                startIcon={askQuestion.isPending ? <CircularProgress size={20} /> : <Send />}
              >
                {askQuestion.isPending ? 'Asking...' : 'Ask Question'}
              </Button>
            </form>
          </Paper>

          {/* Current Answer */}
          {askQuestion.data && (
            <Paper sx={{ p: 4, bgcolor: 'primary.light' }}>
              <Typography variant="h6" gutterBottom color="primary.dark">
                Answer:
              </Typography>
              <Typography variant="body1" sx={{ whiteSpace: 'pre-wrap', color: 'text.primary' }}>
                {askQuestion.data.answer}
              </Typography>

              {askQuestion.data.sources && askQuestion.data.sources.length > 0 && (
                <Box sx={{ mt: 3 }}>
                  <Typography variant="subtitle2" color="text.secondary" gutterBottom>
                    Sources:
                  </Typography>
                  <Box sx={{ display: 'flex', gap: 1, flexWrap: 'wrap' }}>
                    {askQuestion.data.sources.map((source, index) => (
                      <Chip
                        key={index}
                        label={source}
                        size="small"
                        variant="outlined"
                        color="primary"
                      />
                    ))}
                  </Box>
                </Box>
              )}
            </Paper>
          )}
        </Box>

        {/* History Sidebar */}
        <Box sx={{ width: { xs: '100%', md: 400 } }}>
          <Card>
            <CardContent>
              <Box
                sx={{
                  display: 'flex',
                  justifyContent: 'space-between',
                  alignItems: 'center',
                  mb: 2,
                }}
              >
                <Box sx={{ display: 'flex', alignItems: 'center', flex: 1 }}>
                  <History sx={{ mr: 1 }} />
                  <Typography variant="h6">Question History</Typography>
                  {selectedChapter && (
                    <Chip
                      label="Filtered"
                      size="small"
                      color="primary"
                      sx={{ ml: 1 }}
                      onDelete={() => setSelectedChapter('')}
                    />
                  )}
                </Box>
                <IconButton size="small" onClick={() => setShowHistory(!showHistory)}>
                  {showHistory ? <ExpandLess /> : <ExpandMore />}
                </IconButton>
              </Box>

              <Collapse in={showHistory}>
                {historyLoading && (
                  <Box sx={{ textAlign: 'center', py: 3 }}>
                    <CircularProgress size={40} />
                  </Box>
                )}

                {!historyLoading && history && history.length === 0 && (
                  <Box sx={{ textAlign: 'center', py: 3 }}>
                    <Typography variant="body2" color="text.secondary">
                      No questions asked yet
                    </Typography>
                  </Box>
                )}

                {!historyLoading && history && history.length > 0 && (
                  <Box sx={{ maxHeight: 600, overflow: 'auto' }}>
                    {history.map((item, index) => (
                      <Box key={item.id || index}>
                        <Box sx={{ py: 2 }}>
                          <Box sx={{ display: 'flex', alignItems: 'center', gap: 1, mb: 1 }}>
                            <AccessTime sx={{ fontSize: 16, color: 'text.secondary' }} />
                            <Typography variant="caption" color="text.secondary">
                              {new Date(item.created_at).toLocaleDateString()} at{' '}
                              {new Date(item.created_at).toLocaleTimeString()}
                            </Typography>
                          </Box>

                          <Typography
                            variant="body2"
                            fontWeight="medium"
                            sx={{ mb: 1, cursor: 'pointer' }}
                            onClick={() => setQuestion(item.question)}
                          >
                            Q: {item.question}
                          </Typography>

                          <Typography variant="body2" color="text.secondary" sx={{ fontSize: '0.875rem' }}>
                            A: {item.answer.substring(0, 150)}
                            {item.answer.length > 150 ? '...' : ''}
                          </Typography>
                        </Box>
                        {index < history.length - 1 && <Divider />}
                      </Box>
                    ))}
                  </Box>
                )}
              </Collapse>
            </CardContent>
          </Card>

          {/* Tips */}
          <Card sx={{ mt: 2 }}>
            <CardContent>
              <Typography variant="subtitle2" gutterBottom>
                Tips for Better Answers
              </Typography>
              <Typography variant="body2" color="text.secondary" paragraph>
                • Be specific with your medical questions
              </Typography>
              <Typography variant="body2" color="text.secondary" paragraph>
                • Include relevant clinical context
              </Typography>
              <Typography variant="body2" color="text.secondary" paragraph>
                • Click on previous questions to reuse them
              </Typography>
              <Typography variant="body2" color="text.secondary">
                • Answers are AI-generated and should be verified
              </Typography>
            </CardContent>
          </Card>
        </Box>
      </Box>
    </Container>
  )
}
