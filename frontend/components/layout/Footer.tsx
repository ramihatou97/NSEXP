'use client'

import { Box, Container, Typography, Link as MuiLink, Grid } from '@mui/material'
import { GitHub, Email, Description } from '@mui/icons-material'

export function Footer() {
  return (
    <Box component="footer" sx={{ bgcolor: 'grey.900', color: 'white', py: 6, mt: 'auto' }}>
      <Container maxWidth="lg">
        <Grid container spacing={4}>
          <Grid item xs={12} sm={6} md={4}>
            <Typography variant="h6" gutterBottom>
              NeuroKnowledge
            </Typography>
            <Typography variant="body2" sx={{ color: 'grey.400' }}>
              Advanced AI-powered neurosurgical knowledge management system for personal use.
            </Typography>
          </Grid>
          
          <Grid item xs={12} sm={6} md={4}>
            <Typography variant="h6" gutterBottom>
              Quick Links
            </Typography>
            <Box sx={{ display: 'flex', flexDirection: 'column', gap: 1 }}>
              <MuiLink href="/library" color="inherit" underline="hover">
                Chapter Library
              </MuiLink>
              <MuiLink href="/synthesis" color="inherit" underline="hover">
                AI Synthesis
              </MuiLink>
              <MuiLink href="/search" color="inherit" underline="hover">
                Search
              </MuiLink>
              <MuiLink href="/qa" color="inherit" underline="hover">
                Q&A Assistant
              </MuiLink>
            </Box>
          </Grid>
          
          <Grid item xs={12} sm={12} md={4}>
            <Typography variant="h6" gutterBottom>
              Resources
            </Typography>
            <Box sx={{ display: 'flex', flexDirection: 'column', gap: 1 }}>
              <MuiLink href="http://localhost:8000/api/docs" target="_blank" color="inherit" underline="hover">
                <Description sx={{ fontSize: 16, verticalAlign: 'middle', mr: 0.5 }} />
                API Documentation
              </MuiLink>
              <MuiLink href="https://github.com/ramihatou97/NNP" target="_blank" color="inherit" underline="hover">
                <GitHub sx={{ fontSize: 16, verticalAlign: 'middle', mr: 0.5 }} />
                GitHub Repository
              </MuiLink>
            </Box>
          </Grid>
        </Grid>
        
        <Box sx={{ mt: 4, pt: 3, borderTop: '1px solid rgba(255, 255, 255, 0.1)' }}>
          <Typography variant="body2" align="center" sx={{ color: 'grey.500' }}>
            © 2024 Neurosurgical Knowledge System. For personal use only.
          </Typography>
        </Box>
      </Container>
    </Box>
  )
}
