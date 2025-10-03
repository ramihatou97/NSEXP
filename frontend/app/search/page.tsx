'use client'

import { useState } from 'react'
import {
  Container,
  Typography,
  Box,
  TextField,
  Button,
  Paper,
  Card,
  CardContent,
  Chip,
  Tabs,
  Tab,
  CircularProgress,
  Alert,
  Divider,
  IconButton,
  Tooltip,
} from '@mui/material'
import {
  Search as SearchIcon,
  FilterList,
  TrendingUp,
  Article,
  Science,
  MedicalServices,
} from '@mui/icons-material'
import Link from 'next/link'
import { useSearch, useSemanticSearch } from '@/lib/hooks'
import type { SearchResult } from '@/lib/types'

type SearchType = 'all' | 'chapters' | 'references' | 'procedures'
type SearchMode = 'basic' | 'semantic'

export default function SearchPage() {
  const [query, setQuery] = useState('')
  const [searchType, setSearchType] = useState<SearchType>('all')
  const [searchMode, setSearchMode] = useState<SearchMode>('basic')
  const [submitted, setSubmitted] = useState(false)

  // Basic search
  const basicSearch = useSearch(
    {
      query,
      search_type: searchType,
      limit: 50,
    },
    {
      enabled: submitted && searchMode === 'basic' && query.length > 0,
    }
  )

  // Semantic search
  const semanticSearch = useSemanticSearch(
    {
      query,
      limit: 20,
    },
    {
      enabled: submitted && searchMode === 'semantic' && query.length > 0,
    }
  )

  const currentSearch = searchMode === 'basic' ? basicSearch : semanticSearch

  const handleSearch = (e: React.FormEvent) => {
    e.preventDefault()
    if (query.trim()) {
      setSubmitted(true)
    }
  }

  const handleReset = () => {
    setQuery('')
    setSubmitted(false)
    setSearchType('all')
  }

  const getResultIcon = (type: string) => {
    switch (type) {
      case 'chapter':
        return <Article />
      case 'reference':
        return <Science />
      case 'procedure':
        return <MedicalServices />
      default:
        return <Article />
    }
  }

  const getResultColor = (type: string) => {
    switch (type) {
      case 'chapter':
        return 'primary'
      case 'reference':
        return 'secondary'
      case 'procedure':
        return 'success'
      default:
        return 'default'
    }
  }

  return (
    <Container maxWidth="lg" sx={{ py: 4 }}>
      {/* Header */}
      <Box sx={{ mb: 4 }}>
        <Typography variant="h3" gutterBottom>
          <SearchIcon sx={{ verticalAlign: 'middle', mr: 1, fontSize: 40 }} />
          Search
        </Typography>
        <Typography variant="body1" color="text.secondary">
          Search across chapters, references, and procedures
        </Typography>
      </Box>

      {/* Search Form */}
      <Paper sx={{ p: 3, mb: 4 }}>
        <form onSubmit={handleSearch}>
          <Box sx={{ display: 'flex', gap: 2, mb: 2 }}>
            <TextField
              fullWidth
              placeholder="Search neurosurgical topics, procedures, or keywords..."
              value={query}
              onChange={(e) => {
                setQuery(e.target.value)
                if (submitted) setSubmitted(false)
              }}
              autoFocus
            />
            <Button
              type="submit"
              variant="contained"
              startIcon={<SearchIcon />}
              disabled={!query.trim()}
              sx={{ minWidth: 120 }}
            >
              Search
            </Button>
          </Box>

          {/* Search Options */}
          <Box sx={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
            <Tabs
              value={searchType}
              onChange={(_, newValue) => {
                setSearchType(newValue)
                if (submitted) setSubmitted(false)
              }}
              variant="scrollable"
            >
              <Tab label="All" value="all" />
              <Tab label="Chapters" value="chapters" />
              <Tab label="References" value="references" />
              <Tab label="Procedures" value="procedures" />
            </Tabs>

            <Chip
              label={searchMode === 'basic' ? 'Basic Search' : 'AI Semantic Search'}
              icon={searchMode === 'semantic' ? <TrendingUp /> : <SearchIcon />}
              onClick={() => {
                setSearchMode(searchMode === 'basic' ? 'semantic' : 'basic')
                if (submitted) setSubmitted(false)
              }}
              color={searchMode === 'semantic' ? 'primary' : 'default'}
              clickable
            />
          </Box>
        </form>
      </Paper>

      {/* Loading State */}
      {currentSearch.isLoading && (
        <Box sx={{ display: 'flex', justifyContent: 'center', py: 8 }}>
          <CircularProgress />
        </Box>
      )}

      {/* Error State */}
      {currentSearch.error && (
        <Alert severity="error" sx={{ mb: 3 }}>
          Search failed: {currentSearch.error.message}
          <Button onClick={() => currentSearch.refetch()} sx={{ ml: 2 }}>
            Retry
          </Button>
        </Alert>
      )}

      {/* Results */}
      {submitted && !currentSearch.isLoading && !currentSearch.error && (
        <>
          {/* Results Header */}
          <Box sx={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', mb: 3 }}>
            <Typography variant="h6">
              {currentSearch.data?.length || 0} result(s) found
              {searchMode === 'semantic' && (
                <Chip
                  label="AI-Powered"
                  size="small"
                  color="primary"
                  sx={{ ml: 1 }}
                />
              )}
            </Typography>
            {currentSearch.data && currentSearch.data.length > 0 && (
              <Button size="small" onClick={handleReset}>
                Clear Search
              </Button>
            )}
          </Box>

          {/* Empty State */}
          {(!currentSearch.data || currentSearch.data.length === 0) && (
            <Paper sx={{ p: 6, textAlign: 'center' }}>
              <SearchIcon sx={{ fontSize: 64, color: 'text.secondary', mb: 2 }} />
              <Typography variant="h6" color="text.secondary" gutterBottom>
                No results found
              </Typography>
              <Typography variant="body2" color="text.secondary">
                Try different keywords or use semantic search for better results
              </Typography>
            </Paper>
          )}

          {/* Results List */}
          {currentSearch.data && currentSearch.data.length > 0 && (
            <Box sx={{ display: 'flex', flexDirection: 'column', gap: 2 }}>
              {currentSearch.data.map((result: SearchResult) => (
                <Card
                  key={result.id}
                  component={Link}
                  href={result.url || '#'}
                  sx={{
                    textDecoration: 'none',
                    transition: 'all 0.2s',
                    '&:hover': {
                      boxShadow: 4,
                      transform: 'translateY(-2px)',
                    },
                  }}
                >
                  <CardContent>
                    <Box sx={{ display: 'flex', alignItems: 'start', gap: 2 }}>
                      <Box
                        sx={{
                          display: 'flex',
                          alignItems: 'center',
                          justifyContent: 'center',
                          width: 48,
                          height: 48,
                          borderRadius: 1,
                          bgcolor: `${getResultColor(result.type)}.light`,
                          color: `${getResultColor(result.type)}.main`,
                        }}
                      >
                        {getResultIcon(result.type)}
                      </Box>

                      <Box sx={{ flex: 1 }}>
                        <Box sx={{ display: 'flex', alignItems: 'center', gap: 1, mb: 0.5 }}>
                          <Chip
                            label={result.type}
                            size="small"
                            color={getResultColor(result.type)}
                          />
                          {searchMode === 'semantic' && (
                            <Chip
                              label={`${Math.round(result.relevance_score * 100)}% match`}
                              size="small"
                              variant="outlined"
                            />
                          )}
                        </Box>

                        <Typography variant="h6" gutterBottom>
                          {result.title}
                        </Typography>

                        <Typography
                          variant="body2"
                          color="text.secondary"
                          sx={{
                            display: '-webkit-box',
                            WebkitLineClamp: 2,
                            WebkitBoxOrient: 'vertical',
                            overflow: 'hidden',
                          }}
                        >
                          {result.snippet}
                        </Typography>

                        {result.metadata && Object.keys(result.metadata).length > 0 && (
                          <Box sx={{ mt: 1, display: 'flex', gap: 0.5, flexWrap: 'wrap' }}>
                            {Object.entries(result.metadata)
                              .slice(0, 3)
                              .map(([key, value]) => (
                                <Chip
                                  key={key}
                                  label={`${key}: ${value}`}
                                  size="small"
                                  variant="outlined"
                                />
                              ))}
                          </Box>
                        )}
                      </Box>
                    </Box>
                  </CardContent>
                </Card>
              ))}
            </Box>
          )}
        </>
      )}

      {/* Empty Initial State */}
      {!submitted && (
        <Paper sx={{ p: 6, textAlign: 'center' }}>
          <SearchIcon sx={{ fontSize: 64, color: 'text.secondary', mb: 2 }} />
          <Typography variant="h6" color="text.secondary" gutterBottom>
            Start Your Search
          </Typography>
          <Typography variant="body2" color="text.secondary">
            Enter keywords to search across all neurosurgical content
          </Typography>
          <Box sx={{ mt: 3, display: 'flex', gap: 1, justifyContent: 'center', flexWrap: 'wrap' }}>
            <Chip
              label="Try: Glioblastoma"
              onClick={() => {
                setQuery('Glioblastoma')
                setSubmitted(true)
              }}
              clickable
            />
            <Chip
              label="Try: Aneurysm clipping"
              onClick={() => {
                setQuery('Aneurysm clipping')
                setSubmitted(true)
              }}
              clickable
            />
            <Chip
              label="Try: Spinal fusion"
              onClick={() => {
                setQuery('Spinal fusion')
                setSubmitted(true)
              }}
              clickable
            />
          </Box>
        </Paper>
      )}
    </Container>
  )
}
