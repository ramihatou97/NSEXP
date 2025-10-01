'use client'

import { Card, CardContent, Typography, Chip, Box, Grid } from '@mui/material'
import { AccessTime, Category } from '@mui/icons-material'
import Link from 'next/link'

export function RecentChapters() {
  // Placeholder - will be populated with actual data
  return (
    <Grid container spacing={3}>
      <Grid item xs={12}>
        <Box sx={{ textAlign: 'center', py: 8 }}>
          <Typography variant="h6" color="text.secondary" gutterBottom>
            No chapters yet
          </Typography>
          <Typography variant="body2" color="text.secondary" paragraph>
            Start by creating your first chapter or synthesizing content from references
          </Typography>
          <Box sx={{ display: 'flex', gap: 2, justifyContent: 'center', mt: 2 }}>
            <Link href="/synthesis" style={{ textDecoration: 'none' }}>
              <Chip
                label="Start Synthesis"
                color="primary"
                clickable
              />
            </Link>
            <Link href="/library" style={{ textDecoration: 'none' }}>
              <Chip
                label="Browse Library"
                variant="outlined"
                clickable
              />
            </Link>
          </Box>
        </Box>
      </Grid>
    </Grid>
  )
}
