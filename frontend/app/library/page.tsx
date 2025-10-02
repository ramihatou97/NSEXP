'use client'

import { useState } from 'react'
import {
  Container,
  Typography,
  Box,
  Button,
  Grid,
  Card,
  CardContent,
  CardActions,
  Chip,
  CircularProgress,
  Alert,
  TextField,
  MenuItem,
  IconButton,
  Tooltip,
} from '@mui/material'
import {
  MenuBook,
  Add,
  Edit,
  Delete,
  Visibility,
  FilterList,
  Upload,
} from '@mui/icons-material'
import Link from 'next/link'
import { useChapters, useDeleteChapter } from '@/lib/hooks'
import type { Chapter } from '@/lib/types'

const SPECIALTIES = [
  'All',
  'Neurosurgery General',
  'Brain Tumors',
  'Vascular Neurosurgery',
  'Spine Surgery',
  'Functional Neurosurgery',
  'Pediatric Neurosurgery',
  'Trauma',
  'Skull Base',
]

const STATUS_OPTIONS = ['all', 'draft', 'published', 'archived']

export default function LibraryPage() {
  const [selectedSpecialty, setSelectedSpecialty] = useState('All')
  const [selectedStatus, setSelectedStatus] = useState('all')

  // Fetch chapters from API
  const { data: chapters, isLoading, error, refetch } = useChapters({
    specialty: selectedSpecialty === 'All' ? undefined : selectedSpecialty,
    status: selectedStatus === 'all' ? undefined : selectedStatus,
    limit: 100,
  })

  const deleteChapter = useDeleteChapter()

  const handleDelete = async (id: string) => {
    if (confirm('Are you sure you want to delete this chapter?')) {
      try {
        await deleteChapter.mutateAsync(id)
      } catch (error) {
        console.error('Failed to delete chapter:', error)
      }
    }
  }

  const getStatusColor = (status: string) => {
    switch (status) {
      case 'published':
        return 'success'
      case 'draft':
        return 'warning'
      case 'archived':
        return 'default'
      default:
        return 'info'
    }
  }

  return (
    <Container maxWidth="lg" sx={{ py: 4 }}>
      {/* Header */}
      <Box sx={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', mb: 4 }}>
        <Box>
          <Typography variant="h3" gutterBottom>
            <MenuBook sx={{ verticalAlign: 'middle', mr: 1, fontSize: 40 }} />
            Chapter Library
          </Typography>
          <Typography variant="body1" color="text.secondary">
            Manage your neurosurgical knowledge chapters
          </Typography>
        </Box>
        <Box sx={{ display: 'flex', gap: 2 }}>
          <Button
            variant="outlined"
            startIcon={<Upload />}
            component={Link}
            href="/library/import"
          >
            Import
          </Button>
          <Button
            variant="contained"
            startIcon={<Add />}
            component={Link}
            href="/synthesis"
          >
            New Chapter
          </Button>
        </Box>
      </Box>

      {/* Filters */}
      <Box sx={{ mb: 3, display: 'flex', gap: 2 }}>
        <TextField
          select
          label="Specialty"
          value={selectedSpecialty}
          onChange={(e) => setSelectedSpecialty(e.target.value)}
          sx={{ minWidth: 200 }}
          size="small"
        >
          {SPECIALTIES.map((specialty) => (
            <MenuItem key={specialty} value={specialty}>
              {specialty}
            </MenuItem>
          ))}
        </TextField>

        <TextField
          select
          label="Status"
          value={selectedStatus}
          onChange={(e) => setSelectedStatus(e.target.value)}
          sx={{ minWidth: 150 }}
          size="small"
        >
          {STATUS_OPTIONS.map((status) => (
            <MenuItem key={status} value={status}>
              {status.charAt(0).toUpperCase() + status.slice(1)}
            </MenuItem>
          ))}
        </TextField>
      </Box>

      {/* Loading State */}
      {isLoading && (
        <Box sx={{ display: 'flex', justifyContent: 'center', py: 8 }}>
          <CircularProgress />
        </Box>
      )}

      {/* Error State */}
      {error && (
        <Alert severity="error" sx={{ mb: 3 }}>
          Failed to load chapters: {error.message}
          <Button onClick={() => refetch()} sx={{ ml: 2 }}>
            Retry
          </Button>
        </Alert>
      )}

      {/* Empty State */}
      {!isLoading && !error && chapters && chapters.length === 0 && (
        <Box sx={{ textAlign: 'center', py: 8 }}>
          <MenuBook sx={{ fontSize: 64, color: 'text.secondary', mb: 2 }} />
          <Typography variant="h6" color="text.secondary" gutterBottom>
            No chapters yet
          </Typography>
          <Typography variant="body2" color="text.secondary" paragraph>
            Start by creating your first chapter through AI synthesis
          </Typography>
          <Button
            variant="contained"
            component={Link}
            href="/synthesis"
            sx={{ mt: 2 }}
          >
            Start Synthesis
          </Button>
        </Box>
      )}

      {/* Chapters Grid */}
      {!isLoading && !error && chapters && chapters.length > 0 && (
        <Grid container spacing={3}>
          {chapters.map((chapter) => (
            <Grid item xs={12} md={6} lg={4} key={chapter.id}>
              <Card sx={{ height: '100%', display: 'flex', flexDirection: 'column' }}>
                <CardContent sx={{ flexGrow: 1 }}>
                  <Box sx={{ display: 'flex', justifyContent: 'space-between', mb: 1 }}>
                    <Chip
                      label={chapter.status}
                      color={getStatusColor(chapter.status)}
                      size="small"
                    />
                    <Typography variant="caption" color="text.secondary">
                      v{chapter.version}
                    </Typography>
                  </Box>

                  <Typography variant="h6" component="h3" gutterBottom>
                    {chapter.title}
                  </Typography>

                  <Typography variant="body2" color="text.secondary" gutterBottom>
                    {chapter.specialty}
                  </Typography>

                  {chapter.metadata?.tags && chapter.metadata.tags.length > 0 && (
                    <Box sx={{ mt: 1, display: 'flex', gap: 0.5, flexWrap: 'wrap' }}>
                      {chapter.metadata.tags.slice(0, 3).map((tag) => (
                        <Chip key={tag} label={tag} size="small" variant="outlined" />
                      ))}
                    </Box>
                  )}

                  <Typography variant="caption" color="text.secondary" sx={{ display: 'block', mt: 2 }}>
                    Updated: {new Date(chapter.updated_at).toLocaleDateString()}
                  </Typography>
                </CardContent>

                <CardActions sx={{ justifyContent: 'space-between', px: 2, pb: 2 }}>
                  <Box>
                    <Tooltip title="View">
                      <IconButton
                        size="small"
                        component={Link}
                        href={`/library/${chapter.id}`}
                      >
                        <Visibility />
                      </IconButton>
                    </Tooltip>
                    <Tooltip title="Edit">
                      <IconButton
                        size="small"
                        component={Link}
                        href={`/library/${chapter.id}/edit`}
                      >
                        <Edit />
                      </IconButton>
                    </Tooltip>
                  </Box>
                  <Tooltip title="Delete">
                    <IconButton
                      size="small"
                      color="error"
                      onClick={() => handleDelete(chapter.id)}
                      disabled={deleteChapter.isPending}
                    >
                      <Delete />
                    </IconButton>
                  </Tooltip>
                </CardActions>
              </Card>
            </Grid>
          ))}
        </Grid>
      )}

      {/* Chapter Count */}
      {!isLoading && chapters && chapters.length > 0 && (
        <Typography variant="body2" color="text.secondary" sx={{ mt: 3, textAlign: 'center' }}>
          Showing {chapters.length} chapter{chapters.length !== 1 ? 's' : ''}
        </Typography>
      )}
    </Container>
  )
}
