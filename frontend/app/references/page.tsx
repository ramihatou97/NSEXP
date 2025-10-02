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
  IconButton,
  Tooltip,
  Dialog,
  DialogTitle,
  DialogContent,
  DialogActions,
} from '@mui/material'
import {
  Science,
  Add,
  Edit,
  Delete,
  Link as LinkIcon,
  FileCopy,
} from '@mui/icons-material'
import Link from 'next/link'
import { useReferences, useCreateReference, useDeleteReference } from '@/lib/hooks'
import type { CreateReferenceRequest } from '@/lib/types'

export default function ReferencesPage() {
  const [openDialog, setOpenDialog] = useState(false)
  const [formData, setFormData] = useState<CreateReferenceRequest>({
    title: '',
    authors: [],
    year: new Date().getFullYear(),
    journal: '',
    doi: '',
    pmid: '',
  })
  const [authorInput, setAuthorInput] = useState('')

  const { data: references, isLoading, error, refetch } = useReferences({ limit: 100 })
  const createReference = useCreateReference()
  const deleteReference = useDeleteReference()

  const handleOpenDialog = () => {
    setOpenDialog(true)
  }

  const handleCloseDialog = () => {
    setOpenDialog(false)
    setFormData({
      title: '',
      authors: [],
      year: new Date().getFullYear(),
      journal: '',
      doi: '',
      pmid: '',
    })
    setAuthorInput('')
  }

  const handleAddAuthor = () => {
    if (authorInput.trim()) {
      setFormData({
        ...formData,
        authors: [...formData.authors, authorInput.trim()],
      })
      setAuthorInput('')
    }
  }

  const handleRemoveAuthor = (index: number) => {
    setFormData({
      ...formData,
      authors: formData.authors.filter((_, i) => i !== index),
    })
  }

  const handleSubmit = async () => {
    if (!formData.title || formData.authors.length === 0) {
      return
    }

    try {
      await createReference.mutateAsync(formData)
      handleCloseDialog()
    } catch (error) {
      console.error('Failed to create reference:', error)
    }
  }

  const handleDelete = async (id: string) => {
    if (confirm('Are you sure you want to delete this reference?')) {
      try {
        await deleteReference.mutateAsync(id)
      } catch (error) {
        console.error('Failed to delete reference:', error)
      }
    }
  }

  const copyToClipboard = (text: string) => {
    navigator.clipboard.writeText(text)
  }

  return (
    <Container maxWidth="lg" sx={{ py: 4 }}>
      {/* Header */}
      <Box sx={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', mb: 4 }}>
        <Box>
          <Typography variant="h3" gutterBottom>
            <Science sx={{ verticalAlign: 'middle', mr: 1, fontSize: 40 }} />
            Reference Library
          </Typography>
          <Typography variant="body1" color="text.secondary">
            Manage your medical literature and citations
          </Typography>
        </Box>
        <Button
          variant="contained"
          startIcon={<Add />}
          onClick={handleOpenDialog}
        >
          Add Reference
        </Button>
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
          Failed to load references: {error.message}
          <Button onClick={() => refetch()} sx={{ ml: 2 }}>
            Retry
          </Button>
        </Alert>
      )}

      {/* Empty State */}
      {!isLoading && !error && references && references.length === 0 && (
        <Box sx={{ textAlign: 'center', py: 8 }}>
          <Science sx={{ fontSize: 64, color: 'text.secondary', mb: 2 }} />
          <Typography variant="h6" color="text.secondary" gutterBottom>
            No references yet
          </Typography>
          <Typography variant="body2" color="text.secondary" paragraph>
            Start building your reference library
          </Typography>
          <Button
            variant="contained"
            onClick={handleOpenDialog}
            sx={{ mt: 2 }}
          >
            Add First Reference
          </Button>
        </Box>
      )}

      {/* References Grid */}
      {!isLoading && !error && references && references.length > 0 && (
        <>
          <Grid container spacing={3}>
            {references.map((reference) => (
              <Grid item xs={12} key={reference.id}>
                <Card>
                  <CardContent>
                    <Box sx={{ display: 'flex', justifyContent: 'space-between', alignItems: 'start' }}>
                      <Box sx={{ flex: 1 }}>
                        <Typography variant="h6" gutterBottom>
                          {reference.title}
                        </Typography>

                        <Typography variant="body2" color="text.secondary" gutterBottom>
                          {reference.authors.join(', ')}
                        </Typography>

                        <Box sx={{ display: 'flex', gap: 1, mt: 2, flexWrap: 'wrap' }}>
                          <Chip label={reference.year} size="small" />
                          {reference.journal && (
                            <Chip label={reference.journal} size="small" variant="outlined" />
                          )}
                          {reference.doi && (
                            <Chip
                              label={`DOI: ${reference.doi}`}
                              size="small"
                              variant="outlined"
                              icon={<LinkIcon />}
                              onClick={() => window.open(`https://doi.org/${reference.doi}`, '_blank')}
                              clickable
                            />
                          )}
                          {reference.pmid && (
                            <Chip
                              label={`PMID: ${reference.pmid}`}
                              size="small"
                              variant="outlined"
                              icon={<LinkIcon />}
                              onClick={() => window.open(`https://pubmed.ncbi.nlm.nih.gov/${reference.pmid}`, '_blank')}
                              clickable
                            />
                          )}
                          {reference.citation_count !== undefined && (
                            <Chip
                              label={`${reference.citation_count} citations`}
                              size="small"
                              color="primary"
                              variant="outlined"
                            />
                          )}
                        </Box>

                        {reference.abstract && (
                          <Typography
                            variant="body2"
                            sx={{
                              mt: 2,
                              display: '-webkit-box',
                              WebkitLineClamp: 3,
                              WebkitBoxOrient: 'vertical',
                              overflow: 'hidden',
                            }}
                          >
                            {reference.abstract}
                          </Typography>
                        )}
                      </Box>

                      <Box sx={{ display: 'flex', flexDirection: 'column', gap: 1, ml: 2 }}>
                        <Tooltip title="Copy Citation">
                          <IconButton
                            size="small"
                            onClick={() => {
                              const citation = `${reference.authors.join(', ')} (${reference.year}). ${reference.title}. ${reference.journal || ''}.`
                              copyToClipboard(citation)
                            }}
                          >
                            <FileCopy />
                          </IconButton>
                        </Tooltip>
                        <Tooltip title="View Details">
                          <IconButton
                            size="small"
                            component={Link}
                            href={`/references/${reference.id}`}
                          >
                            <LinkIcon />
                          </IconButton>
                        </Tooltip>
                        <Tooltip title="Delete">
                          <IconButton
                            size="small"
                            color="error"
                            onClick={() => handleDelete(reference.id)}
                            disabled={deleteReference.isPending}
                          >
                            <Delete />
                          </IconButton>
                        </Tooltip>
                      </Box>
                    </Box>
                  </CardContent>
                </Card>
              </Grid>
            ))}
          </Grid>

          <Typography variant="body2" color="text.secondary" sx={{ mt: 3, textAlign: 'center' }}>
            Showing {references.length} reference{references.length !== 1 ? 's' : ''}
          </Typography>
        </>
      )}

      {/* Add Reference Dialog */}
      <Dialog open={openDialog} onClose={handleCloseDialog} maxWidth="md" fullWidth>
        <DialogTitle>Add New Reference</DialogTitle>
        <DialogContent>
          <Box sx={{ display: 'flex', flexDirection: 'column', gap: 2, mt: 2 }}>
            <TextField
              fullWidth
              label="Title *"
              value={formData.title}
              onChange={(e) => setFormData({ ...formData, title: e.target.value })}
              required
            />

            <Box>
              <Typography variant="subtitle2" gutterBottom>
                Authors *
              </Typography>
              <Box sx={{ display: 'flex', gap: 1, mb: 1 }}>
                <TextField
                  size="small"
                  fullWidth
                  placeholder="Author name"
                  value={authorInput}
                  onChange={(e) => setAuthorInput(e.target.value)}
                  onKeyPress={(e) => {
                    if (e.key === 'Enter') {
                      e.preventDefault()
                      handleAddAuthor()
                    }
                  }}
                />
                <Button onClick={handleAddAuthor} variant="outlined">
                  Add
                </Button>
              </Box>
              <Box sx={{ display: 'flex', gap: 0.5, flexWrap: 'wrap' }}>
                {formData.authors.map((author, index) => (
                  <Chip
                    key={index}
                    label={author}
                    onDelete={() => handleRemoveAuthor(index)}
                    size="small"
                  />
                ))}
              </Box>
            </Box>

            <TextField
              fullWidth
              label="Year *"
              type="number"
              value={formData.year}
              onChange={(e) => setFormData({ ...formData, year: parseInt(e.target.value) })}
              required
            />

            <TextField
              fullWidth
              label="Journal"
              value={formData.journal}
              onChange={(e) => setFormData({ ...formData, journal: e.target.value })}
            />

            <TextField
              fullWidth
              label="DOI"
              value={formData.doi}
              onChange={(e) => setFormData({ ...formData, doi: e.target.value })}
              placeholder="10.1000/example"
            />

            <TextField
              fullWidth
              label="PMID"
              value={formData.pmid}
              onChange={(e) => setFormData({ ...formData, pmid: e.target.value })}
              placeholder="12345678"
            />
          </Box>
        </DialogContent>
        <DialogActions>
          <Button onClick={handleCloseDialog}>Cancel</Button>
          <Button
            onClick={handleSubmit}
            variant="contained"
            disabled={!formData.title || formData.authors.length === 0 || createReference.isPending}
          >
            {createReference.isPending ? 'Adding...' : 'Add Reference'}
          </Button>
        </DialogActions>
      </Dialog>
    </Container>
  )
}
