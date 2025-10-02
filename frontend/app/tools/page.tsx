'use client'

import { Container, Typography, Box, Paper, Grid, Card, CardContent } from '@mui/material'
import { MedicalServices, Calculate, Biotech, AutoGraph } from '@mui/icons-material'

const tools = [
  {
    title: 'Surgical Planning',
    description: 'Plan surgical approaches and trajectories',
    icon: MedicalServices,
    status: 'Coming Soon',
  },
  {
    title: 'Clinical Calculators',
    description: 'GCS, Hunt-Hess, Fisher scales, and more',
    icon: Calculate,
    status: 'Coming Soon',
  },
  {
    title: 'Neuronavigation',
    description: 'Virtual navigation and anatomy visualization',
    icon: Biotech,
    status: 'Coming Soon',
  },
  {
    title: 'Outcome Prediction',
    description: 'AI-powered surgical outcome prediction',
    icon: AutoGraph,
    status: 'Coming Soon',
  },
]

export default function ToolsPage() {
  return (
    <Container maxWidth="lg" sx={{ py: 4 }}>
      <Box sx={{ mb: 4 }}>
        <Typography variant="h3" gutterBottom>
          <MedicalServices sx={{ verticalAlign: 'middle', mr: 1, fontSize: 40 }} />
          Clinical Tools
        </Typography>
        <Typography variant="body1" color="text.secondary">
          Access surgical planning, neuronavigation, and decision support tools
        </Typography>
      </Box>

      <Grid container spacing={3}>
        {tools.map((tool) => (
          <Grid item xs={12} md={6} key={tool.title}>
            <Card sx={{ height: '100%' }}>
              <CardContent>
                <Box sx={{ display: 'flex', alignItems: 'center', mb: 2 }}>
                  <tool.icon sx={{ fontSize: 40, mr: 2, color: 'primary.main' }} />
                  <Box>
                    <Typography variant="h6">{tool.title}</Typography>
                    <Typography variant="caption" color="warning.main">
                      {tool.status}
                    </Typography>
                  </Box>
                </Box>
                <Typography variant="body2" color="text.secondary">
                  {tool.description}
                </Typography>
              </CardContent>
            </Card>
          </Grid>
        ))}
      </Grid>
    </Container>
  )
}
