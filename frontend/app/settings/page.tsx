'use client'

import { useState, useEffect } from 'react'
import {
  Container,
  Typography,
  Box,
  Paper,
  Tabs,
  Tab,
  TextField,
  Button,
  MenuItem,
  Switch,
  FormControlLabel,
  Slider,
  Alert,
  CircularProgress,
  Divider,
  Grid,
} from '@mui/material'
import {
  Settings as SettingsIcon,
  Psychology,
  Palette,
  Language,
  Notifications,
  Save,
} from '@mui/icons-material'
import { usePreferences, useUpdatePreferences } from '@/lib/hooks'
import type { UserPreferences } from '@/lib/types'

interface TabPanelProps {
  children?: React.ReactNode
  index: number
  value: number
}

function TabPanel(props: TabPanelProps) {
  const { children, value, index, ...other } = props
  return (
    <div hidden={value !== index} {...other}>
      {value === index && <Box sx={{ py: 3 }}>{children}</Box>}
    </div>
  )
}

export default function SettingsPage() {
  const [tabValue, setTabValue] = useState(0)
  const { data: preferences, isLoading } = usePreferences()
  const updatePreferences = useUpdatePreferences()

  const [formData, setFormData] = useState<UserPreferences | null>(null)

  // Initialize form with preferences
  useEffect(() => {
    if (preferences) {
      setFormData(preferences)
    }
  }, [preferences])

  const handleSave = async () => {
    if (!formData) return

    try {
      await updatePreferences.mutateAsync(formData)
    } catch (error) {
      console.error('Failed to save preferences:', error)
    }
  }

  if (isLoading || !formData) {
    return (
      <Container maxWidth="lg" sx={{ py: 4, textAlign: 'center' }}>
        <CircularProgress size={60} />
      </Container>
    )
  }

  return (
    <Container maxWidth="lg" sx={{ py: 4 }}>
      {/* Header */}
      <Box sx={{ mb: 4 }}>
        <Typography variant="h3" gutterBottom>
          <SettingsIcon sx={{ verticalAlign: 'middle', mr: 1, fontSize: 40 }} />
          Settings & Preferences
        </Typography>
        <Typography variant="body1" color="text.secondary">
          Customize your experience and AI settings
        </Typography>
      </Box>

      {/* Success/Error Messages */}
      {updatePreferences.isSuccess && (
        <Alert severity="success" sx={{ mb: 3 }} onClose={() => updatePreferences.reset()}>
          Preferences saved successfully!
        </Alert>
      )}

      {updatePreferences.isError && (
        <Alert severity="error" sx={{ mb: 3 }} onClose={() => updatePreferences.reset()}>
          Failed to save preferences. Please try again.
        </Alert>
      )}

      <Paper>
        {/* Tabs */}
        <Tabs
          value={tabValue}
          onChange={(_, newValue) => setTabValue(newValue)}
          sx={{ borderBottom: 1, borderColor: 'divider' }}
        >
          <Tab icon={<Psychology />} label="AI Settings" iconPosition="start" />
          <Tab icon={<Palette />} label="Display" iconPosition="start" />
          <Tab icon={<Language />} label="Defaults" iconPosition="start" />
          <Tab icon={<Notifications />} label="Notifications" iconPosition="start" />
        </Tabs>

        {/* AI Settings Panel */}
        <TabPanel value={tabValue} index={0}>
          <Box sx={{ px: 3 }}>
            <Typography variant="h6" gutterBottom>
              AI Model Preferences
            </Typography>

            <TextField
              select
              fullWidth
              label="Default AI Model"
              value={formData.ai_settings.default_model}
              onChange={(e) =>
                setFormData({
                  ...formData,
                  ai_settings: {
                    ...formData.ai_settings,
                    default_model: e.target.value as any,
                  },
                })
              }
              sx={{ mb: 3 }}
            >
              <MenuItem value="openai">OpenAI GPT-4</MenuItem>
              <MenuItem value="anthropic">Anthropic Claude</MenuItem>
              <MenuItem value="gemini">Google Gemini</MenuItem>
              <MenuItem value="perplexity">Perplexity</MenuItem>
            </TextField>

            <Typography gutterBottom>Temperature: {formData.ai_settings.temperature}</Typography>
            <Slider
              value={formData.ai_settings.temperature}
              onChange={(_, value) =>
                setFormData({
                  ...formData,
                  ai_settings: {
                    ...formData.ai_settings,
                    temperature: value as number,
                  },
                })
              }
              min={0}
              max={1}
              step={0.1}
              marks
              valueLabelDisplay="auto"
              sx={{ mb: 3 }}
            />

            <TextField
              fullWidth
              type="number"
              label="Max Tokens"
              value={formData.ai_settings.max_tokens}
              onChange={(e) =>
                setFormData({
                  ...formData,
                  ai_settings: {
                    ...formData.ai_settings,
                    max_tokens: parseInt(e.target.value) || 2000,
                  },
                })
              }
              sx={{ mb: 3 }}
            />

            <FormControlLabel
              control={
                <Switch
                  checked={formData.ai_settings.enable_citations}
                  onChange={(e) =>
                    setFormData({
                      ...formData,
                      ai_settings: {
                        ...formData.ai_settings,
                        enable_citations: e.target.checked,
                      },
                    })
                  }
                />
              }
              label="Enable automatic citations in AI responses"
            />
          </Box>
        </TabPanel>

        {/* Display Settings Panel */}
        <TabPanel value={tabValue} index={1}>
          <Box sx={{ px: 3 }}>
            <Typography variant="h6" gutterBottom>
              Display Preferences
            </Typography>

            <TextField
              select
              fullWidth
              label="Theme"
              value={formData.display_settings.theme}
              onChange={(e) =>
                setFormData({
                  ...formData,
                  display_settings: {
                    ...formData.display_settings,
                    theme: e.target.value as any,
                  },
                })
              }
              sx={{ mb: 3 }}
            >
              <MenuItem value="light">Light</MenuItem>
              <MenuItem value="dark">Dark</MenuItem>
              <MenuItem value="auto">Auto (System)</MenuItem>
            </TextField>

            <TextField
              select
              fullWidth
              label="Font Size"
              value={formData.display_settings.font_size}
              onChange={(e) =>
                setFormData({
                  ...formData,
                  display_settings: {
                    ...formData.display_settings,
                    font_size: e.target.value as any,
                  },
                })
              }
              sx={{ mb: 3 }}
            >
              <MenuItem value="small">Small</MenuItem>
              <MenuItem value="medium">Medium</MenuItem>
              <MenuItem value="large">Large</MenuItem>
            </TextField>

            <FormControlLabel
              control={
                <Switch
                  checked={formData.display_settings.compact_mode}
                  onChange={(e) =>
                    setFormData({
                      ...formData,
                      display_settings: {
                        ...formData.display_settings,
                        compact_mode: e.target.checked,
                      },
                    })
                  }
                />
              }
              label="Compact mode (denser layout)"
              sx={{ mb: 2 }}
            />

            <FormControlLabel
              control={
                <Switch
                  checked={formData.display_settings.show_preview}
                  onChange={(e) =>
                    setFormData({
                      ...formData,
                      display_settings: {
                        ...formData.display_settings,
                        show_preview: e.target.checked,
                      },
                    })
                  }
                />
              }
              label="Show content previews"
            />
          </Box>
        </TabPanel>

        {/* Default Settings Panel */}
        <TabPanel value={tabValue} index={2}>
          <Box sx={{ px: 3 }}>
            <Typography variant="h6" gutterBottom>
              Default Settings
            </Typography>

            <TextField
              select
              fullWidth
              label="Default Specialty"
              value={formData.default_settings.specialty}
              onChange={(e) =>
                setFormData({
                  ...formData,
                  default_settings: {
                    ...formData.default_settings,
                    specialty: e.target.value,
                  },
                })
              }
              sx={{ mb: 3 }}
            >
              <MenuItem value="Neurosurgery General">Neurosurgery General</MenuItem>
              <MenuItem value="Brain Tumors">Brain Tumors</MenuItem>
              <MenuItem value="Vascular Neurosurgery">Vascular Neurosurgery</MenuItem>
              <MenuItem value="Spine Surgery">Spine Surgery</MenuItem>
              <MenuItem value="Functional Neurosurgery">Functional Neurosurgery</MenuItem>
              <MenuItem value="Pediatric Neurosurgery">Pediatric Neurosurgery</MenuItem>
              <MenuItem value="Trauma">Trauma</MenuItem>
              <MenuItem value="Skull Base">Skull Base</MenuItem>
            </TextField>

            <TextField
              select
              fullWidth
              label="Citation Style"
              value={formData.default_settings.citation_style}
              onChange={(e) =>
                setFormData({
                  ...formData,
                  default_settings: {
                    ...formData.default_settings,
                    citation_style: e.target.value as any,
                  },
                })
              }
              sx={{ mb: 3 }}
            >
              <MenuItem value="vancouver">Vancouver</MenuItem>
              <MenuItem value="apa">APA</MenuItem>
              <MenuItem value="mla">MLA</MenuItem>
              <MenuItem value="chicago">Chicago</MenuItem>
            </TextField>

            <TextField
              select
              fullWidth
              label="Language"
              value={formData.default_settings.language}
              onChange={(e) =>
                setFormData({
                  ...formData,
                  default_settings: {
                    ...formData.default_settings,
                    language: e.target.value,
                  },
                })
              }
              sx={{ mb: 3 }}
            >
              <MenuItem value="en">English</MenuItem>
              <MenuItem value="es">Spanish</MenuItem>
              <MenuItem value="fr">French</MenuItem>
              <MenuItem value="de">German</MenuItem>
            </TextField>
          </Box>
        </TabPanel>

        {/* Notification Settings Panel */}
        <TabPanel value={tabValue} index={3}>
          <Box sx={{ px: 3 }}>
            <Typography variant="h6" gutterBottom>
              Notification Preferences
            </Typography>

            <FormControlLabel
              control={
                <Switch
                  checked={formData.notification_settings.email_notifications}
                  onChange={(e) =>
                    setFormData({
                      ...formData,
                      notification_settings: {
                        ...formData.notification_settings,
                        email_notifications: e.target.checked,
                      },
                    })
                  }
                />
              }
              label="Enable email notifications"
              sx={{ mb: 2 }}
            />

            <FormControlLabel
              control={
                <Switch
                  checked={formData.notification_settings.synthesis_complete}
                  onChange={(e) =>
                    setFormData({
                      ...formData,
                      notification_settings: {
                        ...formData.notification_settings,
                        synthesis_complete: e.target.checked,
                      },
                    })
                  }
                />
              }
              label="Notify when synthesis is complete"
              sx={{ mb: 2 }}
            />

            <FormControlLabel
              control={
                <Switch
                  checked={formData.notification_settings.gap_detection}
                  onChange={(e) =>
                    setFormData({
                      ...formData,
                      notification_settings: {
                        ...formData.notification_settings,
                        gap_detection: e.target.checked,
                      },
                    })
                  }
                />
              }
              label="Notify when knowledge gaps are detected"
            />
          </Box>
        </TabPanel>

        {/* Save Button */}
        <Divider />
        <Box sx={{ p: 3, display: 'flex', justifyContent: 'flex-end' }}>
          <Button
            variant="contained"
            size="large"
            startIcon={updatePreferences.isPending ? <CircularProgress size={20} /> : <Save />}
            onClick={handleSave}
            disabled={updatePreferences.isPending}
          >
            {updatePreferences.isPending ? 'Saving...' : 'Save Preferences'}
          </Button>
        </Box>
      </Paper>
    </Container>
  )
}
