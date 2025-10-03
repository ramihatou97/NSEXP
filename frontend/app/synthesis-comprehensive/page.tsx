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
  Chip,
  Card,
  CardContent,
  Grid,
  Accordion,
  AccordionSummary,
  AccordionDetails,
  LinearProgress,
  Stack,
} from '@mui/material'
import {
  AutoAwesome,
  ExpandMore,
  CheckCircle,
  Description,
  Timer,
  Assessment,
} from '@mui/icons-material'
import {
  synthesizeComprehensiveChapter,
  ComprehensiveSynthesisRequest,
  ComprehensiveSynthesisResponse,
} from '@/lib/api/enhanced-services'

const specialties = [
  'TUMOR',
  'VASCULAR',
  'SPINE',
  'FUNCTIONAL',
  'PEDIATRIC',
  'TRAUMA',
  'PERIPHERAL_NERVE',
  'SKULL_BASE',
  'ENDOSCOPIC',
  'STEREOTACTIC',
]

export default function ComprehensiveSynthesisPage() {
  const [topic, setTopic] = useState('')
  const [specialty, setSpecialty] = useState('TUMOR')
  const [focusAreas, setFocusAreas] = useState('')
  const [includeImages, setIncludeImages] = useState(true)
  const [loading, setLoading] = useState(false)
  const [result, setResult] = useState<ComprehensiveSynthesisResponse | null>(null)
  const [error, setError] = useState<string | null>(null)

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault()
    setLoading(true)
    setError(null)
    setResult(null)

    try {
      const request: ComprehensiveSynthesisRequest = {
        topic,
        specialty,
        references: [],
        focus_areas: focusAreas ? focusAreas.split(',').map(s => s.trim()) : undefined,
        include_images: includeImages,
      }

      const response = await synthesizeComprehensiveChapter(request)
      setResult(response)
    } catch (err: any) {
      setError(err.message || 'Failed to generate comprehensive chapter')
    } finally {
      setLoading(false)
    }
  }

  return (
    <Container maxWidth="xl" sx={{ py: 4 }}>
      <Typography variant="h3" gutterBottom sx={{ display: 'flex', alignItems: 'center', gap: 2 }}>
        <AutoAwesome fontSize="large" />
        Comprehensive Chapter Synthesis
      </Typography>
      <Typography variant="subtitle1" color="text.secondary" paragraph>
        Generate neurosurgical chapters with 150+ comprehensive sections covering all aspects
      </Typography>

      <Grid container spacing={3}>
        <Grid item xs={12} md={4}>
          <Paper sx={{ p: 3 }}>
            <Typography variant="h6" gutterBottom>
              Chapter Configuration
            </Typography>

            <Box component="form" onSubmit={handleSubmit} sx={{ mt: 2 }}>
              <TextField
                fullWidth
                label="Topic"
                value={topic}
                onChange={(e) => setTopic(e.target.value)}
                required
                margin="normal"
                placeholder="e.g., Glioblastoma Multiforme"
                helperText="Enter the neurosurgical topic"
              />

              <TextField
                fullWidth
                select
                label="Specialty"
                value={specialty}
                onChange={(e) => setSpecialty(e.target.value)}
                required
                margin="normal"
              >
                {specialties.map((spec) => (
                  <MenuItem key={spec} value={spec}>
                    {spec.replace(/_/g, ' ')}
                  </MenuItem>
                ))}
              </TextField>

              <TextField
                fullWidth
                label="Focus Areas (optional)"
                value={focusAreas}
                onChange={(e) => setFocusAreas(e.target.value)}
                margin="normal"
                placeholder="Surgical Techniques, Molecular Biology"
                helperText="Comma-separated sections to emphasize"
              />

              <Box sx={{ mt: 2, mb: 2 }}>
                <Button
                  variant="outlined"
                  size="small"
                  onClick={() => setIncludeImages(!includeImages)}
                  color={includeImages ? 'primary' : 'inherit'}
                >
                  {includeImages ? 'Images: ON' : 'Images: OFF'}
                </Button>
              </Box>

              <Button
                type="submit"
                variant="contained"
                fullWidth
                disabled={loading || !topic}
                size="large"
                startIcon={loading ? <CircularProgress size={20} /> : <AutoAwesome />}
              >
                {loading ? 'Generating...' : 'Generate Comprehensive Chapter'}
              </Button>
            </Box>

            {loading && (
              <Box sx={{ mt: 3 }}>
                <Typography variant="body2" color="text.secondary" gutterBottom>
                  This may take 30-60 seconds...
                </Typography>
                <LinearProgress />
              </Box>
            )}
          </Paper>
        </Grid>

        <Grid item xs={12} md={8}>
          {error && (
            <Alert severity="error" sx={{ mb: 2 }}>
              {error}
            </Alert>
          )}

          {result && result.success && (
            <Box>
              <Paper sx={{ p: 3, mb: 2 }}>
                <Typography variant="h5" gutterBottom>
                  {result.topic}
                </Typography>
                <Stack direction="row" spacing={1} sx={{ mb: 2 }}>
                  <Chip
                    icon={<Description />}
                    label={`${result.section_count} sections`}
                    color="primary"
                    size="small"
                  />
                  <Chip
                    icon={<Assessment />}
                    label={`${result.total_words.toLocaleString()} words`}
                    size="small"
                  />
                  <Chip
                    icon={<Timer />}
                    label={`${result.quality_metrics.estimated_reading_time_minutes} min read`}
                    size="small"
                  />
                  <Chip
                    icon={<CheckCircle />}
                    label={`${Math.round(result.quality_metrics.completeness_score * 100)}% complete`}
                    color="success"
                    size="small"
                  />
                </Stack>

                <Grid container spacing={2} sx={{ mb: 2 }}>
                  <Grid item xs={6} sm={3}>
                    <Card variant="outlined">
                      <CardContent>
                        <Typography variant="h4" color="primary">
                          {result.reference_count}
                        </Typography>
                        <Typography variant="caption" color="text.secondary">
                          References
                        </Typography>
                      </CardContent>
                    </Card>
                  </Grid>
                  <Grid item xs={6} sm={3}>
                    <Card variant="outlined">
                      <CardContent>
                        <Typography variant="h4" color="primary">
                          {result.image_count}
                        </Typography>
                        <Typography variant="caption" color="text.secondary">
                          Images
                        </Typography>
                      </CardContent>
                    </Card>
                  </Grid>
                  <Grid item xs={6} sm={3}>
                    <Card variant="outlined">
                      <CardContent>
                        <Typography variant="h4" color="primary">
                          {result.quality_metrics.average_section_length}
                        </Typography>
                        <Typography variant="caption" color="text.secondary">
                          Avg Words/Section
                        </Typography>
                      </CardContent>
                    </Card>
                  </Grid>
                  <Grid item xs={6} sm={3}>
                    <Card variant="outlined">
                      <CardContent>
                        <Typography variant="h4" color="primary">
                          {(result.quality_metrics.reference_density * 1000).toFixed(1)}
                        </Typography>
                        <Typography variant="caption" color="text.secondary">
                          Citations/1000 words
                        </Typography>
                      </CardContent>
                    </Card>
                  </Grid>
                </Grid>
              </Paper>

              <Typography variant="h6" gutterBottom sx={{ mt: 3 }}>
                Chapter Sections ({result.section_count})
              </Typography>

              {Object.entries(result.sections).map(([section, content], index) => (
                <Accordion key={index} sx={{ mb: 1 }}>
                  <AccordionSummary expandIcon={<ExpandMore />}>
                    <Typography variant="subtitle1" fontWeight="medium">
                      {section}
                    </Typography>
                    <Chip
                      label={`${content.split(' ').length} words`}
                      size="small"
                      sx={{ ml: 2 }}
                    />
                  </AccordionSummary>
                  <AccordionDetails>
                    <Typography
                      variant="body2"
                      sx={{
                        whiteSpace: 'pre-wrap',
                        fontFamily: 'Georgia, serif',
                        lineHeight: 1.8,
                      }}
                    >
                      {content}
                    </Typography>
                  </AccordionDetails>
                </Accordion>
              ))}

              {result.references && result.references.length > 0 && (
                <Paper sx={{ p: 3, mt: 3 }}>
                  <Typography variant="h6" gutterBottom>
                    References ({result.references.length})
                  </Typography>
                  <Box component="ol" sx={{ pl: 2 }}>
                    {result.references.map((ref, index) => (
                      <Typography
                        key={index}
                        component="li"
                        variant="body2"
                        sx={{ mb: 1 }}
                      >
                        {ref}
                      </Typography>
                    ))}
                  </Box>
                </Paper>
              )}
            </Box>
          )}
        </Grid>
      </Grid>
    </Container>
  )
}
