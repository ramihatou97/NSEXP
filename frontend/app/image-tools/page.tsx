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
  Grid,
  Card,
  CardContent,
  CardMedia,
  Chip,
  Stack,
  Tabs,
  Tab,
} from '@mui/material'
import {
  Image as ImageIcon,
  PhotoLibrary,
  Biotech,
  Download,
} from '@mui/icons-material'
import {
  extractImagesFromPDF,
  analyzeAnatomicalImage,
  ExtractedImage,
  ImageExtractionResponse,
} from '@/lib/api/enhanced-services'

interface TabPanelProps {
  children?: React.ReactNode
  index: number
  value: number
}

function TabPanel(props: TabPanelProps) {
  const { children, value, index, ...other } = props
  return (
    <div
      role="tabpanel"
      hidden={value !== index}
      {...other}
    >
      {value === index && <Box sx={{ py: 3 }}>{children}</Box>}
    </div>
  )
}

export default function ImageToolsPage() {
  const [tabValue, setTabValue] = useState(0)
  const [pdfPath, setPdfPath] = useState('')
  const [loading, setLoading] = useState(false)
  const [extractionResult, setExtractionResult] = useState<ImageExtractionResponse | null>(null)
  const [error, setError] = useState<string | null>(null)

  const handleExtraction = async () => {
    setLoading(true)
    setError(null)
    setExtractionResult(null)

    try {
      const response = await extractImagesFromPDF({
        pdf_path: pdfPath,
        extract_text: true,
        min_width: 100,
        min_height: 100,
      })
      setExtractionResult(response)
    } catch (err: any) {
      setError(err.message || 'Failed to extract images')
    } finally {
      setLoading(false)
    }
  }

  return (
    <Container maxWidth="xl" sx={{ py: 4 }}>
      <Typography variant="h3" gutterBottom sx={{ display: 'flex', alignItems: 'center', gap: 2 }}>
        <PhotoLibrary fontSize="large" />
        Medical Image Processing
      </Typography>
      <Typography variant="subtitle1" color="text.secondary" paragraph>
        Extract and analyze medical images from PDFs with OCR and AI-powered classification
      </Typography>

      <Paper sx={{ mb: 3 }}>
        <Tabs
          value={tabValue}
          onChange={(_, newValue) => setTabValue(newValue)}
          indicatorColor="primary"
        >
          <Tab label="Extract Images" />
          <Tab label="Analyze Image" />
        </Tabs>
      </Paper>

      <TabPanel value={tabValue} index={0}>
        <Grid container spacing={3}>
          <Grid item xs={12} md={4}>
            <Paper sx={{ p: 3 }}>
              <Typography variant="h6" gutterBottom>
                PDF Image Extraction
              </Typography>

              <TextField
                fullWidth
                label="PDF Path"
                value={pdfPath}
                onChange={(e) => setPdfPath(e.target.value)}
                placeholder="/textbooks/neurosurgery.pdf"
                margin="normal"
                helperText="Path to PDF file on server"
              />

              <Button
                variant="contained"
                fullWidth
                onClick={handleExtraction}
                disabled={loading || !pdfPath}
                startIcon={loading ? <CircularProgress size={20} /> : <ImageIcon />}
                sx={{ mt: 2 }}
              >
                {loading ? 'Extracting...' : 'Extract Images'}
              </Button>
            </Paper>
          </Grid>

          <Grid item xs={12} md={8}>
            {error && (
              <Alert severity="error" sx={{ mb: 2 }}>
                {error}
              </Alert>
            )}

            {extractionResult && extractionResult.success && (
              <Box>
                <Paper sx={{ p: 3, mb: 2 }}>
                  <Stack direction="row" spacing={2} alignItems="center">
                    <Typography variant="h5">
                      Extraction Results
                    </Typography>
                    <Chip
                      label={`${extractionResult.images_extracted} images`}
                      color="primary"
                    />
                    <Chip
                      label={`${extractionResult.total_pages} pages`}
                    />
                  </Stack>
                </Paper>

                <Grid container spacing={2}>
                  {extractionResult.images.map((image, index) => (
                    <Grid item xs={12} sm={6} md={4} key={index}>
                      <Card>
                        <CardContent>
                          <Typography variant="subtitle2" gutterBottom>
                            Page {image.page_number} - Image {image.image_index}
                          </Typography>
                          <Stack spacing={1}>
                            <Chip
                              label={image.type.replace(/_/g, ' ')}
                              size="small"
                              color="primary"
                              variant="outlined"
                            />
                            <Typography variant="caption" color="text.secondary">
                              {image.width} x {image.height} px
                            </Typography>
                            <Typography variant="caption" color="text.secondary">
                              Format: {image.format.toUpperCase()}
                            </Typography>
                            <Typography variant="caption" color="text.secondary">
                              Size: {(image.size_bytes / 1024).toFixed(1)} KB
                            </Typography>
                            {image.extracted_text && (
                              <Box sx={{ mt: 1 }}>
                                <Typography variant="caption" fontWeight="bold">
                                  OCR Text:
                                </Typography>
                                <Typography variant="caption" display="block">
                                  {image.extracted_text}
                                </Typography>
                              </Box>
                            )}
                          </Stack>
                        </CardContent>
                      </Card>
                    </Grid>
                  ))}
                </Grid>
              </Box>
            )}
          </Grid>
        </Grid>
      </TabPanel>

      <TabPanel value={tabValue} index={1}>
        <Paper sx={{ p: 3 }}>
          <Typography variant="h6" gutterBottom>
            Anatomical Image Analysis
          </Typography>
          <Alert severity="info" sx={{ mt: 2 }}>
            Image analysis feature uses AI vision models to identify anatomical structures.
            Configure AI API keys to enable this feature.
          </Alert>
        </Paper>
      </TabPanel>
    </Container>
  )
}
