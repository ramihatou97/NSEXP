'use client'

import { useState } from 'react'
import { useRouter } from 'next/navigation'
import {
  Container,
  Typography,
  Box,
  Paper,
  Button,
  Alert,
  CircularProgress,
  Card,
  CardContent,
  IconButton,
  Chip,
  List,
  ListItem,
  ListItemText,
  Divider,
} from '@mui/material'
import {
  Upload,
  FileUpload,
  Delete,
  CheckCircle,
  Error as ErrorIcon,
  ArrowBack,
  Code,
  Description,
  InsertDriveFile,
} from '@mui/icons-material'
import { importApi } from '@/lib/api/import'

export default function ImportPage() {
  const router = useRouter()
  const [importFile, setImportFile] = useState<File | null>(null)
  const [importLoading, setImportLoading] = useState(false)
  const [importSuccess, setImportSuccess] = useState<string>('')
  const [importError, setImportError] = useState('')
  const [importedChapterId, setImportedChapterId] = useState<string>('')

  const handleFileSelect = (event: React.ChangeEvent<HTMLInputElement>) => {
    const file = event.target.files?.[0]
    if (file) {
      setImportFile(file)
      setImportError('')
      setImportSuccess('')
      setImportedChapterId('')
    }
  }

  const handleImport = async () => {
    if (!importFile) return

    setImportLoading(true)
    setImportSuccess('')
    setImportError('')

    try {
      const result = await importApi.importChapterFromFile(importFile)

      if (result.success) {
        const chapterId = result.chapter_id || ''
        setImportedChapterId(chapterId)
        setImportSuccess(
          result.message || `Chapter imported successfully! ${chapterId ? `ID: ${chapterId}` : ''}`
        )
        setImportFile(null)
        // Reset file input
        const fileInput = document.getElementById('import-file-input') as HTMLInputElement
        if (fileInput) fileInput.value = ''
      } else {
        setImportError(result.error || 'Import failed')
      }
    } catch (error) {
      setImportError(error instanceof Error ? error.message : 'Import failed')
    } finally {
      setImportLoading(false)
    }
  }

  const getFormatIcon = (format: string) => {
    switch (format) {
      case 'json':
        return <Code />
      case 'markdown':
      case 'md':
        return <Description />
      default:
        return <InsertDriveFile />
    }
  }

  const handleViewChapter = () => {
    if (importedChapterId) {
      router.push(`/library/${importedChapterId}`)
    }
  }

  return (
    <Container maxWidth="md" sx={{ py: 4 }}>
      {/* Back Button */}
      <Button startIcon={<ArrowBack />} onClick={() => router.push('/library')} sx={{ mb: 3 }}>
        Back to Library
      </Button>

      {/* Header */}
      <Box sx={{ mb: 4 }}>
        <Typography variant="h3" gutterBottom>
          <Upload sx={{ verticalAlign: 'middle', mr: 1, fontSize: 40 }} />
          Import Chapter
        </Typography>
        <Typography variant="body1" color="text.secondary">
          Import chapters from JSON or Markdown files
        </Typography>
      </Box>

      <Paper sx={{ p: 4, mb: 3 }}>
        {/* File Selection */}
        <Box sx={{ mb: 3 }}>
          <input
            id="import-file-input"
            type="file"
            accept=".json,.md,.markdown"
            onChange={handleFileSelect}
            style={{ display: 'none' }}
          />
          <label htmlFor="import-file-input">
            <Button
              variant="outlined"
              component="span"
              fullWidth
              size="large"
              startIcon={<Upload />}
              sx={{ mb: 2, py: 3 }}
            >
              Select File (.json, .md, .markdown)
            </Button>
          </label>

          {importFile && (
            <Box
              sx={{
                p: 3,
                border: '2px dashed',
                borderColor: 'primary.main',
                borderRadius: 2,
                bgcolor: 'primary.light',
                display: 'flex',
                alignItems: 'center',
                justifyContent: 'space-between',
              }}
            >
              <Box sx={{ display: 'flex', alignItems: 'center', gap: 2 }}>
                {getFormatIcon(importFile.name.split('.').pop() || '')}
                <Box>
                  <Typography variant="body1" fontWeight="medium">
                    {importFile.name}
                  </Typography>
                  <Chip
                    label={`${(importFile.size / 1024).toFixed(2)} KB`}
                    size="small"
                    variant="outlined"
                    sx={{ mt: 0.5 }}
                  />
                </Box>
              </Box>
              <IconButton
                onClick={() => {
                  setImportFile(null)
                  const fileInput = document.getElementById('import-file-input') as HTMLInputElement
                  if (fileInput) fileInput.value = ''
                }}
              >
                <Delete />
              </IconButton>
            </Box>
          )}
        </Box>

        {/* Success Alert */}
        {importSuccess && (
          <Alert severity="success" icon={<CheckCircle />} sx={{ mb: 2 }}>
            {importSuccess}
            {importedChapterId && (
              <Button onClick={handleViewChapter} sx={{ ml: 2 }} size="small" variant="outlined">
                View Chapter
              </Button>
            )}
          </Alert>
        )}

        {/* Error Alert */}
        {importError && (
          <Alert severity="error" icon={<ErrorIcon />} sx={{ mb: 2 }}>
            {importError}
          </Alert>
        )}

        {/* Import Button */}
        <Button
          variant="contained"
          size="large"
          fullWidth
          startIcon={importLoading ? <CircularProgress size={20} /> : <FileUpload />}
          onClick={handleImport}
          disabled={!importFile || importLoading}
        >
          {importLoading ? 'Importing...' : 'Import Chapter'}
        </Button>
      </Paper>

      {/* Import Guidelines */}
      <Card>
        <CardContent>
          <Typography variant="h6" gutterBottom>
            Import Guidelines
          </Typography>
          <Typography variant="body2" paragraph>
            Supported file formats:
          </Typography>
          <List dense>
            <ListItem>
              <ListItemText
                primary="JSON Files (.json)"
                secondary="Exported from this system or matching the chapter schema. Preserves all data including metadata, sections, and references."
              />
            </ListItem>
            <Divider />
            <ListItem>
              <ListItemText
                primary="Markdown Files (.md, .markdown)"
                secondary="Standard markdown format with H1 for title, H2 for sections, and H3 for subsections. Content will be automatically parsed."
              />
            </ListItem>
          </List>

          <Alert severity="info" sx={{ mt: 2 }}>
            <Typography variant="body2">
              <strong>Tip:</strong> For best results, use JSON files exported from this system.
              Markdown files are parsed automatically but may lose some structure.
            </Typography>
          </Alert>

          <Box sx={{ mt: 3 }}>
            <Typography variant="subtitle2" gutterBottom>
              Example Markdown Structure:
            </Typography>
            <Paper
              sx={{
                p: 2,
                bgcolor: 'grey.100',
                fontFamily: 'monospace',
                fontSize: '0.875rem',
                whiteSpace: 'pre-wrap',
              }}
            >
              {`# Chapter Title

## Summary
Brief summary of the chapter...

## Introduction
Introduction content...

### Subsection 1
Subsection content...`}
            </Paper>
          </Box>
        </CardContent>
      </Card>
    </Container>
  )
}
