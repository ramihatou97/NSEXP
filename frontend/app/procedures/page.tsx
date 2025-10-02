'use client'

import { useState } from 'react'
import {
  Container,
  Typography,
  Box,
  Paper,
  Grid,
  Card,
  CardContent,
  CardActions,
  Button,
  TextField,
  MenuItem,
  Chip,
  CircularProgress,
  Alert,
  List,
  ListItem,
  ListItemText,
  Divider,
  Dialog,
  DialogTitle,
  DialogContent,
  DialogActions,
  Stepper,
  Step,
  StepLabel,
  StepContent,
} from '@mui/material'
import {
  MedicalServices,
  Search,
  Visibility,
  Timer,
  Warning,
  CheckCircle,
} from '@mui/icons-material'
import { useProcedures, useProcedure } from '@/lib/hooks'
import type { SurgicalProcedure } from '@/lib/types'

const complexityColors = {
  basic: 'success',
  intermediate: 'info',
  advanced: 'warning',
  expert: 'error',
} as const

export default function ProceduresPage() {
  const [procedureType, setProcedureType] = useState('')
  const [anatomicalRegion, setAnatomicalRegion] = useState('')
  const [selectedProcedure, setSelectedProcedure] = useState<string | null>(null)

  const { data: procedures, isLoading, error } = useProcedures({
    procedure_type: procedureType || undefined,
    anatomical_region: anatomicalRegion || undefined,
  })

  const {
    data: procedure,
    isLoading: procedureLoading,
  } = useProcedure(selectedProcedure)

  const handleCloseDetail = () => {
    setSelectedProcedure(null)
  }

  return (
    <Container maxWidth="xl" sx={{ py: 4 }}>
      {/* Header */}
      <Box sx={{ mb: 4 }}>
        <Typography variant="h3" gutterBottom>
          <MedicalServices sx={{ verticalAlign: 'middle', mr: 1, fontSize: 40 }} />
          Surgical Procedures Database
        </Typography>
        <Typography variant="body1" color="text.secondary">
          Browse and learn neurosurgical procedures with step-by-step guidance
        </Typography>
      </Box>

      {/* Filters */}
      <Paper sx={{ p: 3, mb: 3 }}>
        <Grid container spacing={2}>
          <Grid item xs={12} md={6}>
            <TextField
              select
              fullWidth
              label="Procedure Type"
              value={procedureType}
              onChange={(e) => setProcedureType(e.target.value)}
            >
              <MenuItem value="">All Types</MenuItem>
              <MenuItem value="craniotomy">Craniotomy</MenuItem>
              <MenuItem value="spine">Spine Surgery</MenuItem>
              <MenuItem value="vascular">Vascular</MenuItem>
              <MenuItem value="functional">Functional</MenuItem>
              <MenuItem value="tumor">Tumor Resection</MenuItem>
            </TextField>
          </Grid>
          <Grid item xs={12} md={6}>
            <TextField
              select
              fullWidth
              label="Anatomical Region"
              value={anatomicalRegion}
              onChange={(e) => setAnatomicalRegion(e.target.value)}
            >
              <MenuItem value="">All Regions</MenuItem>
              <MenuItem value="frontal">Frontal</MenuItem>
              <MenuItem value="temporal">Temporal</MenuItem>
              <MenuItem value="parietal">Parietal</MenuItem>
              <MenuItem value="occipital">Occipital</MenuItem>
              <MenuItem value="cervical">Cervical Spine</MenuItem>
              <MenuItem value="thoracic">Thoracic Spine</MenuItem>
              <MenuItem value="lumbar">Lumbar Spine</MenuItem>
            </TextField>
          </Grid>
        </Grid>
      </Paper>

      {/* Loading State */}
      {isLoading && (
        <Box sx={{ textAlign: 'center', py: 8 }}>
          <CircularProgress size={60} />
          <Typography variant="body2" color="text.secondary" sx={{ mt: 2 }}>
            Loading procedures...
          </Typography>
        </Box>
      )}

      {/* Error State */}
      {error && (
        <Alert severity="error">
          Failed to load procedures. Please try again later.
        </Alert>
      )}

      {/* Procedures Grid */}
      {!isLoading && procedures && (
        <>
          <Typography variant="h6" gutterBottom>
            {procedures.length} Procedure{procedures.length !== 1 ? 's' : ''} Found
          </Typography>

          {procedures.length === 0 && (
            <Paper sx={{ p: 4, textAlign: 'center' }}>
              <Search sx={{ fontSize: 60, color: 'text.secondary', mb: 2 }} />
              <Typography variant="h6" color="text.secondary">
                No procedures found
              </Typography>
              <Typography variant="body2" color="text.secondary">
                Try adjusting your filters
              </Typography>
            </Paper>
          )}

          <Grid container spacing={3}>
            {procedures.map((proc) => (
              <Grid item xs={12} md={6} lg={4} key={proc.id}>
                <Card sx={{ height: '100%', display: 'flex', flexDirection: 'column' }}>
                  <CardContent sx={{ flexGrow: 1 }}>
                    <Box sx={{ display: 'flex', justifyContent: 'space-between', mb: 2 }}>
                      <Chip
                        label={proc.complexity}
                        color={complexityColors[proc.complexity]}
                        size="small"
                      />
                      <Box sx={{ display: 'flex', alignItems: 'center', gap: 0.5 }}>
                        <Timer fontSize="small" color="action" />
                        <Typography variant="caption" color="text.secondary">
                          {proc.duration_minutes} min
                        </Typography>
                      </Box>
                    </Box>

                    <Typography variant="h6" gutterBottom>
                      {proc.name}
                    </Typography>

                    <Typography variant="body2" color="text.secondary" paragraph>
                      {proc.description.substring(0, 150)}
                      {proc.description.length > 150 ? '...' : ''}
                    </Typography>

                    <Box sx={{ display: 'flex', gap: 1, flexWrap: 'wrap', mb: 1 }}>
                      <Chip label={proc.type} size="small" variant="outlined" />
                      <Chip label={proc.anatomical_region} size="small" variant="outlined" />
                    </Box>

                    <Typography variant="caption" color="text.secondary">
                      {proc.steps.length} steps
                    </Typography>
                  </CardContent>

                  <CardActions>
                    <Button
                      size="small"
                      startIcon={<Visibility />}
                      onClick={() => setSelectedProcedure(proc.id)}
                      fullWidth
                    >
                      View Details
                    </Button>
                  </CardActions>
                </Card>
              </Grid>
            ))}
          </Grid>
        </>
      )}

      {/* Procedure Detail Dialog */}
      <Dialog
        open={!!selectedProcedure}
        onClose={handleCloseDetail}
        maxWidth="md"
        fullWidth
      >
        {procedureLoading && (
          <Box sx={{ p: 4, textAlign: 'center' }}>
            <CircularProgress />
          </Box>
        )}

        {procedure && (
          <>
            <DialogTitle>
              <Box sx={{ display: 'flex', alignItems: 'center', gap: 2 }}>
                <MedicalServices color="primary" />
                <Box sx={{ flex: 1 }}>
                  <Typography variant="h5">{procedure.name}</Typography>
                  <Box sx={{ display: 'flex', gap: 1, mt: 1 }}>
                    <Chip
                      label={procedure.complexity}
                      color={complexityColors[procedure.complexity]}
                      size="small"
                    />
                    <Chip
                      label={`${procedure.duration_minutes} minutes`}
                      size="small"
                      variant="outlined"
                    />
                  </Box>
                </Box>
              </Box>
            </DialogTitle>

            <DialogContent dividers>
              {/* Description */}
              <Typography variant="body1" paragraph>
                {procedure.description}
              </Typography>

              {/* Indications */}
              <Typography variant="h6" gutterBottom sx={{ mt: 3 }}>
                <CheckCircle sx={{ verticalAlign: 'middle', mr: 1 }} color="success" />
                Indications
              </Typography>
              <List dense>
                {procedure.indications.map((indication, index) => (
                  <ListItem key={index}>
                    <ListItemText primary={`• ${indication}`} />
                  </ListItem>
                ))}
              </List>

              {/* Contraindications */}
              <Typography variant="h6" gutterBottom sx={{ mt: 3 }}>
                <Warning sx={{ verticalAlign: 'middle', mr: 1 }} color="warning" />
                Contraindications
              </Typography>
              <List dense>
                {procedure.contraindications.map((contraindication, index) => (
                  <ListItem key={index}>
                    <ListItemText primary={`• ${contraindication}`} />
                  </ListItem>
                ))}
              </List>

              {/* Procedure Steps */}
              <Typography variant="h6" gutterBottom sx={{ mt: 3 }}>
                Procedure Steps
              </Typography>
              <Stepper orientation="vertical">
                {procedure.steps.map((step, index) => (
                  <Step key={index} active={true} completed={false}>
                    <StepLabel>
                      <Typography variant="subtitle1" fontWeight="medium">
                        {step.title}
                      </Typography>
                    </StepLabel>
                    <StepContent>
                      <Typography variant="body2" paragraph>
                        {step.description}
                      </Typography>
                      {step.critical_points.length > 0 && (
                        <>
                          <Typography variant="caption" color="error" fontWeight="medium">
                            Critical Points:
                          </Typography>
                          <List dense>
                            {step.critical_points.map((point, i) => (
                              <ListItem key={i}>
                                <ListItemText
                                  primary={`• ${point}`}
                                  primaryTypographyProps={{
                                    variant: 'caption',
                                    color: 'error',
                                  }}
                                />
                              </ListItem>
                            ))}
                          </List>
                        </>
                      )}
                      <Typography variant="caption" color="text.secondary">
                        Estimated time: {step.estimated_time_minutes} minutes
                      </Typography>
                    </StepContent>
                  </Step>
                ))}
              </Stepper>

              {/* Complications */}
              {procedure.complications.length > 0 && (
                <>
                  <Typography variant="h6" gutterBottom sx={{ mt: 3 }}>
                    Potential Complications
                  </Typography>
                  <List dense>
                    {procedure.complications.map((complication, index) => (
                      <ListItem key={index}>
                        <ListItemText primary={`• ${complication}`} />
                      </ListItem>
                    ))}
                  </List>
                </>
              )}
            </DialogContent>

            <DialogActions>
              <Button onClick={handleCloseDetail}>Close</Button>
            </DialogActions>
          </>
        )}
      </Dialog>
    </Container>
  )
}
