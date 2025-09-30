'use client'

import { Grid, Paper, Typography, Box } from '@mui/material'
import { TrendingUp, Book, Psychology, Speed } from '@mui/icons-material'

const stats = [
  { label: 'Chapters', value: '0', icon: Book, color: '#1976d2' },
  { label: 'AI Syntheses', value: '0', icon: Psychology, color: '#4caf50' },
  { label: 'References', value: '0', icon: TrendingUp, color: '#ff9800' },
  { label: 'Q&A Sessions', value: '0', icon: Speed, color: '#f44336' },
]

export function StatisticsSection() {
  return (
    <Grid container spacing={3}>
      {stats.map((stat) => (
        <Grid item xs={12} sm={6} md={3} key={stat.label}>
          <Paper
            sx={{
              p: 3,
              textAlign: 'center',
              transition: 'all 0.3s',
              '&:hover': {
                transform: 'translateY(-4px)',
                boxShadow: 4,
              },
            }}
          >
            <Box
              sx={{
                display: 'flex',
                alignItems: 'center',
                justifyContent: 'center',
                width: 56,
                height: 56,
                borderRadius: '50%',
                bgcolor: `${stat.color}20`,
                mx: 'auto',
                mb: 2,
              }}
            >
              <stat.icon sx={{ fontSize: 32, color: stat.color }} />
            </Box>
            
            <Typography variant="h3" component="div" sx={{ fontWeight: 700, mb: 1 }}>
              {stat.value}
            </Typography>
            
            <Typography variant="body2" color="text.secondary">
              {stat.label}
            </Typography>
          </Paper>
        </Grid>
      ))}
    </Grid>
  )
}
