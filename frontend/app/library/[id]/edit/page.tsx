'use client'

import { useState, useEffect } from 'react'
import { useParams, useRouter } from 'next/navigation'
import {
  Container,
  Typography,
  Box,
  Paper,
  TextField,
  Button,
  CircularProgress,
  Alert,
  MenuItem,
  Chip,
  IconButton,
  Divider,
} from '@mui/material'
import {
  Save,
  Cancel,
  Add,
  Delete,
  ArrowBack,
} from '@mui/icons-material'
import { useChapter, useUpdateChapter } from '@/lib/hooks'
import type { Chapter, UpdateChapterRequest } from '@/lib/types'

const SPECIALTIES = [
  'Neurosurgery General',
  'Brain Tumors',
  'Vascular Neurosurgery',
  'Spine Surgery',
  'Functional Neurosurgery',
  'Pediatric Neurosurgery',
  'Trauma',
  'Skull Base',
]

const STATUS_OPTIONS = ['draft', 'published', 'archived']

export default function ChapterEditPage() {
  const params = useParams()
  const router = useRouter()
  const chapterId = params?.id as string

  const { data: chapter, isLoading, error } = useChapter(chapterId)
  const updateChapter = useUpdateChapter()

  const [formData, setFormData] = useState<{
    title: string
    specialty: string
    status: string
    summary: string
    tags: string[]
    sections: Array<{
      id: string
      title: string
      content: string
      order: number
    }>
  }>({
    title: '',
    specialty: 'Neurosurgery General',
    status: 'draft',
    summary: '',
    tags: [],
    sections: [],
  })

  const [newTag, setNewTag] = useState('')

  // Load chapter data into form
  useEffect(() => {
    if (chapter) {
      setFormData({
        title: chapter.title,
        specialty: chapter.specialty,
        status: chapter.status,
        summary: chapter.content?.summary || '',
        tags: chapter.metadata?.tags || [],
        sections: chapter.content?.sections || [],
      })
    }
  }, [chapter])

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault()

    const updateData: UpdateChapterRequest = {
      title: formData.title,
      specialty: formData.specialty,
      status: formData.status as any,
      content: {
        summary: formData.summary,
        sections: formData.sections,
      },
      metadata: {
        tags: formData.tags,
      },
    }

    try {
      await updateChapter.mutateAsync({
        id: chapterId,
        data: updateData,
      })
      router.push(`/library/${chapterId}`)
    } catch (error) {
      console.error('Failed to update chapter:', error)
    }
  }

  const handleAddTag = () => {
    if (newTag && !formData.tags.includes(newTag)) {
      setFormData({
        ...formData,
        tags: [...formData.tags, newTag],
      })
      setNewTag('')
    }
  }

  const handleRemoveTag = (tagToRemove: string) => {
    setFormData({
      ...formData,
      tags: formData.tags.filter((tag) => tag !== tagToRemove),
    })
  }

  const handleAddSection = () => {
    const newSection = {
      id: `section-${Date.now()}`,
      title: 'New Section',
      content: '',
      order: formData.sections.length,
    }
    setFormData({
      ...formData,
      sections: [...formData.sections, newSection],
    })
  }

  const handleUpdateSection = (index: number, field: string, value: string) => {
    const updatedSections = [...formData.sections]
    updatedSections[index] = {
      ...updatedSections[index],
      [field]: value,
    }
    setFormData({
      ...formData,
      sections: updatedSections,
    })
  }

  const handleRemoveSection = (index: number) => {
    setFormData({
      ...formData,
      sections: formData.sections.filter((_, i) => i !== index),
    })
  }

  if (isLoading) {
    return (
      <Container maxWidth="lg" sx={{ py: 8, textAlign: 'center' }}>
        <CircularProgress />
      </Container>
    )
  }

  if (error || !chapter) {
    return (
      <Container maxWidth="lg" sx={{ py: 4 }}>
        <Alert severity="error">
          Failed to load chapter
          <Button onClick={() => router.push('/library')} sx={{ ml: 2 }}>
            Back to Library
          </Button>
        </Alert>
      </Container>
    )
  }

  return (
    <Container maxWidth="lg" sx={{ py: 4 }}>
      {/* Header */}
      <Box sx={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', mb: 3 }}>
        <Typography variant="h4">
          Edit Chapter
        </Typography>
        <Button
          startIcon={<ArrowBack />}
          onClick={() => router.push(`/library/${chapterId}`)}
        >
          Cancel
        </Button>
      </Box>

      <form onSubmit={handleSubmit}>
        {/* Basic Info */}
        <Paper sx={{ p: 3, mb: 3 }}>
          <Typography variant="h6" gutterBottom>
            Basic Information
          </Typography>
          <Divider sx={{ mb: 3 }} />

          <TextField
            fullWidth
            label="Title"
            value={formData.title}
            onChange={(e) => setFormData({ ...formData, title: e.target.value })}
            required
            sx={{ mb: 3 }}
          />

          <Box sx={{ display: 'flex', gap: 2, mb: 3 }}>
            <TextField
              select
              label="Specialty"
              value={formData.specialty}
              onChange={(e) => setFormData({ ...formData, specialty: e.target.value })}
              sx={{ flex: 1 }}
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
              value={formData.status}
              onChange={(e) => setFormData({ ...formData, status: e.target.value })}
              sx={{ flex: 1 }}
            >
              {STATUS_OPTIONS.map((status) => (
                <MenuItem key={status} value={status}>
                  {status.charAt(0).toUpperCase() + status.slice(1)}
                </MenuItem>
              ))}
            </TextField>
          </Box>

          <TextField
            fullWidth
            label="Summary"
            value={formData.summary}
            onChange={(e) => setFormData({ ...formData, summary: e.target.value })}
            multiline
            rows={3}
            sx={{ mb: 3 }}
          />

          {/* Tags */}
          <Typography variant="subtitle2" gutterBottom>
            Tags
          </Typography>
          <Box sx={{ display: 'flex', gap: 1, mb: 2, flexWrap: 'wrap' }}>
            {formData.tags.map((tag) => (
              <Chip
                key={tag}
                label={tag}
                onDelete={() => handleRemoveTag(tag)}
                size="small"
              />
            ))}
          </Box>
          <Box sx={{ display: 'flex', gap: 1 }}>
            <TextField
              size="small"
              placeholder="Add tag"
              value={newTag}
              onChange={(e) => setNewTag(e.target.value)}
              onKeyPress={(e) => {
                if (e.key === 'Enter') {
                  e.preventDefault()
                  handleAddTag()
                }
              }}
            />
            <Button onClick={handleAddTag} variant="outlined" size="small">
              Add
            </Button>
          </Box>
        </Paper>

        {/* Content Sections */}
        <Paper sx={{ p: 3, mb: 3 }}>
          <Box sx={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', mb: 2 }}>
            <Typography variant="h6">
              Content Sections
            </Typography>
            <Button
              startIcon={<Add />}
              onClick={handleAddSection}
              variant="outlined"
              size="small"
            >
              Add Section
            </Button>
          </Box>
          <Divider sx={{ mb: 3 }} />

          {formData.sections.map((section, index) => (
            <Box key={section.id} sx={{ mb: 3, p: 2, border: '1px solid', borderColor: 'divider', borderRadius: 1 }}>
              <Box sx={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', mb: 2 }}>
                <Typography variant="subtitle1">
                  Section {index + 1}
                </Typography>
                <IconButton
                  size="small"
                  color="error"
                  onClick={() => handleRemoveSection(index)}
                >
                  <Delete />
                </IconButton>
              </Box>

              <TextField
                fullWidth
                label="Section Title"
                value={section.title}
                onChange={(e) => handleUpdateSection(index, 'title', e.target.value)}
                sx={{ mb: 2 }}
              />

              <TextField
                fullWidth
                label="Content"
                value={section.content}
                onChange={(e) => handleUpdateSection(index, 'content', e.target.value)}
                multiline
                rows={8}
                placeholder="Write your content here..."
              />
            </Box>
          ))}

          {formData.sections.length === 0 && (
            <Alert severity="info">
              No sections yet. Click "Add Section" to start writing content.
            </Alert>
          )}
        </Paper>

        {/* Actions */}
        <Box sx={{ display: 'flex', gap: 2, justifyContent: 'flex-end' }}>
          <Button
            variant="outlined"
            onClick={() => router.push(`/library/${chapterId}`)}
          >
            Cancel
          </Button>
          <Button
            type="submit"
            variant="contained"
            startIcon={<Save />}
            disabled={updateChapter.isPending || !formData.title}
          >
            {updateChapter.isPending ? 'Saving...' : 'Save Changes'}
          </Button>
        </Box>

        {updateChapter.isError && (
          <Alert severity="error" sx={{ mt: 2 }}>
            Failed to save changes. Please try again.
          </Alert>
        )}
      </form>
    </Container>
  )
}
