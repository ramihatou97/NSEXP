'use client'

import { useState } from 'react'
import { useParams, useRouter } from 'next/navigation'
import {
  Container,
  Typography,
  Box,
  Paper,
  Chip,
  Button,
  CircularProgress,
  Alert,
  Divider,
  Grid,
  Card,
  CardContent,
  Menu,
  MenuItem,
  ListItemIcon,
  ListItemText,
} from '@mui/material'
import {
  Edit,
  Delete,
  ArrowBack,
  Download,
  Share,
  Bookmark,
  Code,
  Description,
  InsertDriveFile,
} from '@mui/icons-material'
import Link from 'next/link'
import { useChapter, useDeleteChapter } from '@/lib/hooks'
import { exportApi, type ExportFormat } from '@/lib/api/export'

export default function ChapterDetailPage() {
  const params = useParams()
  const router = useRouter()
  const chapterId = params?.id as string

  const { data: chapter, isLoading, error } = useChapter(chapterId)
  const deleteChapter = useDeleteChapter()

  // Export menu state
  const [exportAnchorEl, setExportAnchorEl] = useState<null | HTMLElement>(null)
  const exportMenuOpen = Boolean(exportAnchorEl)

  const handleExportClick = (event: React.MouseEvent<HTMLButtonElement>) => {
    setExportAnchorEl(event.currentTarget)
  }

  const handleExportClose = () => {
    setExportAnchorEl(null)
  }

  const handleExport = async (format: ExportFormat) => {
    try {
      await exportApi.downloadChapter(chapterId, format)
      handleExportClose()
    } catch (error) {
      console.error('Export failed:', error)
      alert('Export failed. Please try again.')
    }
  }

  const handleDelete = async () => {
    if (confirm('Are you sure you want to delete this chapter? This action cannot be undone.')) {
      try {
        await deleteChapter.mutateAsync(chapterId)
        router.push('/library')
      } catch (error) {
        console.error('Failed to delete chapter:', error)
      }
    }
  }

  if (isLoading) {
    return (
      <Container maxWidth="lg" sx={{ py: 8, textAlign: 'center' }}>
        <CircularProgress />
      </Container>
    )
  }

  if (error) {
    return (
      <Container maxWidth="lg" sx={{ py: 4 }}>
        <Alert severity="error">
          Failed to load chapter: {error.message}
          <Button onClick={() => router.push('/library')} sx={{ ml: 2 }}>
            Back to Library
          </Button>
        </Alert>
      </Container>
    )
  }

  if (!chapter) {
    return (
      <Container maxWidth="lg" sx={{ py: 4 }}>
        <Alert severity="warning">
          Chapter not found
          <Button onClick={() => router.push('/library')} sx={{ ml: 2 }}>
            Back to Library
          </Button>
        </Alert>
      </Container>
    )
  }

  const getStatusColor = (status: string) => {
    switch (status) {
      case 'published': return 'success'
      case 'draft': return 'warning'
      case 'archived': return 'default'
      default: return 'info'
    }
  }

  return (
    <Container maxWidth="lg" sx={{ py: 4 }}>
      {/* Back Button */}
      <Button
        startIcon={<ArrowBack />}
        onClick={() => router.push('/library')}
        sx={{ mb: 3 }}
      >
        Back to Library
      </Button>

      {/* Header */}
      <Paper sx={{ p: 4, mb: 3 }}>
        <Box sx={{ display: 'flex', justifyContent: 'space-between', alignItems: 'start', mb: 2 }}>
          <Box sx={{ flex: 1 }}>
            <Box sx={{ display: 'flex', gap: 1, mb: 2 }}>
              <Chip
                label={chapter.status}
                color={getStatusColor(chapter.status)}
                size="small"
              />
              <Chip
                label={`Version ${chapter.version}`}
                variant="outlined"
                size="small"
              />
              <Chip
                label={chapter.specialty}
                variant="outlined"
                size="small"
              />
            </Box>

            <Typography variant="h3" gutterBottom>
              {chapter.title}
            </Typography>

            {chapter.metadata?.tags && chapter.metadata.tags.length > 0 && (
              <Box sx={{ display: 'flex', gap: 0.5, flexWrap: 'wrap', mt: 2 }}>
                {chapter.metadata.tags.map((tag) => (
                  <Chip key={tag} label={tag} size="small" variant="outlined" />
                ))}
              </Box>
            )}
          </Box>

          {/* Actions */}
          <Box sx={{ display: 'flex', gap: 1, flexDirection: 'column' }}>
            <Button
              variant="contained"
              startIcon={<Edit />}
              component={Link}
              href={`/library/${chapterId}/edit`}
            >
              Edit
            </Button>
            <Button
              variant="outlined"
              startIcon={<Download />}
              onClick={handleExportClick}
            >
              Export
            </Button>
            <Menu
              anchorEl={exportAnchorEl}
              open={exportMenuOpen}
              onClose={handleExportClose}
            >
              <MenuItem onClick={() => handleExport('json')}>
                <ListItemIcon>
                  <Code fontSize="small" />
                </ListItemIcon>
                <ListItemText>JSON</ListItemText>
              </MenuItem>
              <MenuItem onClick={() => handleExport('markdown')}>
                <ListItemIcon>
                  <Description fontSize="small" />
                </ListItemIcon>
                <ListItemText>Markdown</ListItemText>
              </MenuItem>
              <MenuItem onClick={() => handleExport('html')}>
                <ListItemIcon>
                  <InsertDriveFile fontSize="small" />
                </ListItemIcon>
                <ListItemText>HTML</ListItemText>
              </MenuItem>
            </Menu>
            <Button
              variant="outlined"
              color="error"
              startIcon={<Delete />}
              onClick={handleDelete}
              disabled={deleteChapter.isPending}
            >
              Delete
            </Button>
          </Box>
        </Box>

        {/* Metadata */}
        <Grid container spacing={2} sx={{ mt: 2 }}>
          <Grid item xs={12} sm={6} md={3}>
            <Typography variant="caption" color="text.secondary">
              Created
            </Typography>
            <Typography variant="body2">
              {new Date(chapter.created_at).toLocaleDateString()}
            </Typography>
          </Grid>
          <Grid item xs={12} sm={6} md={3}>
            <Typography variant="caption" color="text.secondary">
              Last Updated
            </Typography>
            <Typography variant="body2">
              {new Date(chapter.updated_at).toLocaleDateString()}
            </Typography>
          </Grid>
          {chapter.metadata?.estimated_read_time && (
            <Grid item xs={12} sm={6} md={3}>
              <Typography variant="caption" color="text.secondary">
                Read Time
              </Typography>
              <Typography variant="body2">
                {chapter.metadata.estimated_read_time} min
              </Typography>
            </Grid>
          )}
          {chapter.metadata?.views && (
            <Grid item xs={12} sm={6} md={3}>
              <Typography variant="caption" color="text.secondary">
                Views
              </Typography>
              <Typography variant="body2">
                {chapter.metadata.views}
              </Typography>
            </Grid>
          )}
        </Grid>
      </Paper>

      {/* Summary */}
      {chapter.content?.summary && (
        <Paper sx={{ p: 3, mb: 3, bgcolor: 'info.light' }}>
          <Typography variant="h6" gutterBottom>
            Summary
          </Typography>
          <Typography variant="body1">
            {chapter.content.summary}
          </Typography>
        </Paper>
      )}

      {/* Content Sections */}
      <Paper sx={{ p: 4 }}>
        <Typography variant="h5" gutterBottom>
          Content
        </Typography>
        <Divider sx={{ mb: 3 }} />

        {chapter.content?.sections && chapter.content.sections.length > 0 ? (
          chapter.content.sections.map((section, index) => (
            <Box key={section.id} sx={{ mb: 4 }}>
              <Typography variant="h6" gutterBottom>
                {index + 1}. {section.title}
              </Typography>
              <Typography
                variant="body1"
                sx={{ whiteSpace: 'pre-wrap', lineHeight: 1.8 }}
              >
                {section.content}
              </Typography>

              {section.subsections && section.subsections.length > 0 && (
                <Box sx={{ ml: 3, mt: 2 }}>
                  {section.subsections.map((subsection, subIndex) => (
                    <Box key={subsection.id} sx={{ mb: 3 }}>
                      <Typography variant="subtitle1" gutterBottom>
                        {index + 1}.{subIndex + 1} {subsection.title}
                      </Typography>
                      <Typography
                        variant="body2"
                        sx={{ whiteSpace: 'pre-wrap', lineHeight: 1.7 }}
                      >
                        {subsection.content}
                      </Typography>
                    </Box>
                  ))}
                </Box>
              )}
            </Box>
          ))
        ) : (
          <Alert severity="info">
            No content available yet. Click Edit to add content.
          </Alert>
        )}
      </Paper>

      {/* References Section */}
      {chapter.references && chapter.references.length > 0 && (
        <Paper sx={{ p: 4, mt: 3 }}>
          <Typography variant="h5" gutterBottom>
            References
          </Typography>
          <Divider sx={{ mb: 2 }} />
          <Typography variant="body2" color="text.secondary">
            {chapter.references.length} reference(s) cited
          </Typography>
          {/* TODO: Fetch and display actual reference details */}
        </Paper>
      )}
    </Container>
  )
}
