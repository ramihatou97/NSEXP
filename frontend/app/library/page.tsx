'use client'

import { Container, Typography, Box, Button } from '@mui/material'
import { BookOpen, Add } from '@mui/icons-material'
import Link from 'next/link'

export default function LibraryPage() {
  return (
    <Container maxWidth="lg" sx={{ py: 4 }}>
      <Box sx={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', mb: 4 }}>
        <Box>
          <Typography variant="h3" gutterBottom>
            <BookOpen sx={{ verticalAlign: 'middle', mr: 1, fontSize: 40 }} />
            Chapter Library
          </Typography>
          <Typography variant="body1" color="text.secondary">
            Manage your neurosurgical knowledge chapters
          </Typography>
        </Box>
        <Button
          variant="contained"
          startIcon={<Add />}
          component={Link}
          href="/synthesis"
        >
          New Chapter
        </Button>
      </Box>

      <Box sx={{ textAlign: 'center', py: 8 }}>
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
    </Container>
  )
}
