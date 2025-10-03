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
  Chip,
  Stack,
  Link,
  FormGroup,
  FormControlLabel,
  Checkbox,
} from '@mui/material'
import {
  Search as SearchIcon,
  Science,
  Description,
  OpenInNew,
} from '@mui/icons-material'
import {
  deepLiteratureSearch,
  DeepSearchRequest,
  DeepSearchResponse,
  SearchResult,
} from '@/lib/api/enhanced-services'

export default function DeepSearchPage() {
  const [query, setQuery] = useState('')
  const [sources, setSources] = useState({
    pubmed: true,
    arxiv: true,
    scholar: false,
  })
  const [yearMin, setYearMin] = useState('')
  const [yearMax, setYearMax] = useState('')
  const [maxResults, setMaxResults] = useState(20)
  const [loading, setLoading] = useState(false)
  const [result, setResult] = useState<DeepSearchResponse | null>(null)
  const [error, setError] = useState<string | null>(null)

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault()
    setLoading(true)
    setError(null)
    setResult(null)

    try {
      const selectedSources = Object.entries(sources)
        .filter(([_, enabled]) => enabled)
        .map(([source, _]) => source)

      const request: DeepSearchRequest = {
        query,
        sources: selectedSources,
        max_results: maxResults,
        filters: {
          year_min: yearMin ? parseInt(yearMin) : undefined,
          year_max: yearMax ? parseInt(yearMax) : undefined,
        },
      }

      const response = await deepLiteratureSearch(request)
      setResult(response)
    } catch (err: any) {
      setError(err.message || 'Failed to search literature')
    } finally {
      setLoading(false)
    }
  }

  const getSourceIcon = (source: string) => {
    switch (source) {
      case 'pubmed':
        return <Science />
      case 'arxiv':
        return <Description />
      default:
        return <SearchIcon />
    }
  }

  return (
    <Container maxWidth="xl" sx={{ py: 4 }}>
      <Typography variant="h3" gutterBottom sx={{ display: 'flex', alignItems: 'center', gap: 2 }}>
        <SearchIcon fontSize="large" />
        Deep Literature Search
      </Typography>
      <Typography variant="subtitle1" color="text.secondary" paragraph>
        Search across PubMed, arXiv, and other medical databases with intelligent deduplication
      </Typography>

      <Grid container spacing={3}>
        <Grid item xs={12} md={4}>
          <Paper sx={{ p: 3 }}>
            <Typography variant="h6" gutterBottom>
              Search Configuration
            </Typography>

            <Box component="form" onSubmit={handleSubmit} sx={{ mt: 2 }}>
              <TextField
                fullWidth
                label="Search Query"
                value={query}
                onChange={(e) => setQuery(e.target.value)}
                required
                margin="normal"
                placeholder="e.g., glioblastoma immunotherapy"
                helperText="Enter medical search terms"
              />

              <Typography variant="subtitle2" sx={{ mt: 2, mb: 1 }}>
                Data Sources
              </Typography>
              <FormGroup>
                <FormControlLabel
                  control={
                    <Checkbox
                      checked={sources.pubmed}
                      onChange={(e) => setSources({ ...sources, pubmed: e.target.checked })}
                    />
                  }
                  label="PubMed (NCBI)"
                />
                <FormControlLabel
                  control={
                    <Checkbox
                      checked={sources.arxiv}
                      onChange={(e) => setSources({ ...sources, arxiv: e.target.checked })}
                    />
                  }
                  label="arXiv (Preprints)"
                />
                <FormControlLabel
                  control={
                    <Checkbox
                      checked={sources.scholar}
                      onChange={(e) => setSources({ ...sources, scholar: e.target.checked })}
                      disabled
                    />
                  }
                  label="Google Scholar (Coming Soon)"
                />
              </FormGroup>

              <Grid container spacing={2} sx={{ mt: 2 }}>
                <Grid item xs={6}>
                  <TextField
                    fullWidth
                    label="Year Min"
                    type="number"
                    value={yearMin}
                    onChange={(e) => setYearMin(e.target.value)}
                    placeholder="2020"
                  />
                </Grid>
                <Grid item xs={6}>
                  <TextField
                    fullWidth
                    label="Year Max"
                    type="number"
                    value={yearMax}
                    onChange={(e) => setYearMax(e.target.value)}
                    placeholder="2024"
                  />
                </Grid>
              </Grid>

              <TextField
                fullWidth
                label="Max Results"
                type="number"
                value={maxResults}
                onChange={(e) => setMaxResults(parseInt(e.target.value) || 20)}
                margin="normal"
                inputProps={{ min: 1, max: 100 }}
              />

              <Button
                type="submit"
                variant="contained"
                fullWidth
                disabled={loading || !query}
                size="large"
                startIcon={loading ? <CircularProgress size={20} /> : <SearchIcon />}
                sx={{ mt: 2 }}
              >
                {loading ? 'Searching...' : 'Search Literature'}
              </Button>
            </Box>
          </Paper>
        </Grid>

        <Grid item xs={12} md={8}>
          {error && (
            <Alert severity="error" sx={{ mb: 2 }}>
              {error}
            </Alert>
          )}

          {result && (
            <Box>
              <Paper sx={{ p: 3, mb: 2 }}>
                <Stack direction="row" spacing={2} alignItems="center">
                  <Typography variant="h5">
                    Search Results
                  </Typography>
                  <Chip
                    label={`${result.total_results} results`}
                    color="primary"
                  />
                  <Chip
                    label={`${result.sources_searched?.length || 0} sources`}
                  />
                </Stack>
                <Typography variant="caption" color="text.secondary">
                  Query: {result.query}
                </Typography>
              </Paper>

              <Stack spacing={2}>
                {result.results.map((paper, index) => (
                  <Card key={index} variant="outlined">
                    <CardContent>
                      <Stack direction="row" spacing={1} sx={{ mb: 1 }}>
                        <Chip
                          icon={getSourceIcon(paper.source)}
                          label={paper.source.toUpperCase()}
                          size="small"
                          color="primary"
                        />
                        {paper.year && (
                          <Chip
                            label={paper.year}
                            size="small"
                            variant="outlined"
                          />
                        )}
                        {paper.relevance_score && paper.relevance_score > 0 && (
                          <Chip
                            label={`Score: ${paper.relevance_score.toFixed(1)}`}
                            size="small"
                            color="success"
                            variant="outlined"
                          />
                        )}
                      </Stack>

                      <Typography variant="h6" gutterBottom>
                        {paper.title}
                      </Typography>

                      <Typography variant="body2" color="text.secondary" paragraph>
                        {paper.authors.slice(0, 3).join(', ')}
                        {paper.authors.length > 3 && ' et al.'}
                      </Typography>

                      {paper.journal && (
                        <Typography variant="caption" display="block" gutterBottom>
                          <strong>Journal:</strong> {paper.journal}
                        </Typography>
                      )}

                      {paper.abstract && (
                        <Typography variant="body2" paragraph>
                          {paper.abstract.substring(0, 300)}
                          {paper.abstract.length > 300 && '...'}
                        </Typography>
                      )}

                      <Stack direction="row" spacing={2}>
                        {paper.url && (
                          <Link
                            href={paper.url}
                            target="_blank"
                            rel="noopener"
                            sx={{ display: 'flex', alignItems: 'center', gap: 0.5 }}
                          >
                            View Article <OpenInNew fontSize="small" />
                          </Link>
                        )}
                        {paper.doi && (
                          <Typography variant="caption" color="text.secondary">
                            DOI: {paper.doi}
                          </Typography>
                        )}
                        {paper.pmid && (
                          <Typography variant="caption" color="text.secondary">
                            PMID: {paper.pmid}
                          </Typography>
                        )}
                      </Stack>
                    </CardContent>
                  </Card>
                ))}
              </Stack>
            </Box>
          )}
        </Grid>
      </Grid>
    </Container>
  )
}
