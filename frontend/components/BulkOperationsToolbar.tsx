import { useState } from 'react'
import {
  Box,
  Toolbar,
  Typography,
  IconButton,
  Tooltip,
  Button,
  Dialog,
  DialogTitle,
  DialogContent,
  DialogActions,
  TextField,
  MenuItem,
  Chip,
  Alert,
} from '@mui/material'
import {
  Delete,
  Edit,
  Close,
  CheckCircle,
} from '@mui/icons-material'

const STATUS_OPTIONS = ['published', 'draft', 'archived']

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

interface BulkOperationsToolbarProps {
  selectedCount: number
  onDelete: () => Promise<void>
  onUpdateStatus: (status: string) => Promise<void>
  onUpdateSpecialty: (specialty: string) => Promise<void>
  onClearSelection: () => void
}

export default function BulkOperationsToolbar({
  selectedCount,
  onDelete,
  onUpdateStatus,
  onUpdateSpecialty,
  onClearSelection,
}: BulkOperationsToolbarProps) {
  const [deleteDialogOpen, setDeleteDialogOpen] = useState(false)
  const [updateDialogOpen, setUpdateDialogOpen] = useState(false)
  const [updateField, setUpdateField] = useState<'status' | 'specialty'>('status')
  const [newStatus, setNewStatus] = useState('')
  const [newSpecialty, setNewSpecialty] = useState('')
  const [loading, setLoading] = useState(false)

  if (selectedCount === 0) return null

  const handleDelete = async () => {
    setLoading(true)
    try {
      await onDelete()
      setDeleteDialogOpen(false)
      onClearSelection()
    } catch (error) {
      // Error handling done in parent
    } finally {
      setLoading(false)
    }
  }

  const handleUpdate = async () => {
    setLoading(true)
    try {
      if (updateField === 'status' && newStatus) {
        await onUpdateStatus(newStatus)
      } else if (updateField === 'specialty' && newSpecialty) {
        await onUpdateSpecialty(newSpecialty)
      }
      setUpdateDialogOpen(false)
      onClearSelection()
      setNewStatus('')
      setNewSpecialty('')
    } catch (error) {
      // Error handling done in parent
    } finally {
      setLoading(false)
    }
  }

  return (
    <>
      <Toolbar
        sx={{
          pl: 2,
          pr: 1,
          bgcolor: 'primary.light',
          color: 'primary.contrastText',
          borderRadius: 1,
          mb: 2,
        }}
      >
        <Typography sx={{ flex: '1 1 100%' }} variant="subtitle1" component="div">
          {selectedCount} {selectedCount === 1 ? 'item' : 'items'} selected
        </Typography>

        <Tooltip title="Update">
          <IconButton
            onClick={() => {
              setUpdateField('status')
              setUpdateDialogOpen(true)
            }}
            sx={{ color: 'inherit' }}
          >
            <Edit />
          </IconButton>
        </Tooltip>

        <Tooltip title="Delete">
          <IconButton
            onClick={() => setDeleteDialogOpen(true)}
            sx={{ color: 'inherit' }}
          >
            <Delete />
          </IconButton>
        </Tooltip>

        <Tooltip title="Clear selection">
          <IconButton onClick={onClearSelection} sx={{ color: 'inherit' }}>
            <Close />
          </IconButton>
        </Tooltip>
      </Toolbar>

      {/* Delete Confirmation Dialog */}
      <Dialog open={deleteDialogOpen} onClose={() => !loading && setDeleteDialogOpen(false)}>
        <DialogTitle>Confirm Bulk Delete</DialogTitle>
        <DialogContent>
          <Alert severity="warning" sx={{ mb: 2 }}>
            This action cannot be undone!
          </Alert>
          <Typography>
            Are you sure you want to delete {selectedCount} {selectedCount === 1 ? 'chapter' : 'chapters'}?
          </Typography>
        </DialogContent>
        <DialogActions>
          <Button onClick={() => setDeleteDialogOpen(false)} disabled={loading}>
            Cancel
          </Button>
          <Button
            onClick={handleDelete}
            color="error"
            variant="contained"
            disabled={loading}
            startIcon={loading ? <></> : <Delete />}
          >
            {loading ? 'Deleting...' : 'Delete All'}
          </Button>
        </DialogActions>
      </Dialog>

      {/* Update Dialog */}
      <Dialog
        open={updateDialogOpen}
        onClose={() => !loading && setUpdateDialogOpen(false)}
        maxWidth="sm"
        fullWidth
      >
        <DialogTitle>Bulk Update</DialogTitle>
        <DialogContent>
          <Typography variant="body2" color="text.secondary" sx={{ mb: 3 }}>
            Update {selectedCount} {selectedCount === 1 ? 'chapter' : 'chapters'}
          </Typography>

          <TextField
            select
            fullWidth
            label="Update Field"
            value={updateField}
            onChange={(e) => setUpdateField(e.target.value as 'status' | 'specialty')}
            sx={{ mb: 3 }}
          >
            <MenuItem value="status">Status</MenuItem>
            <MenuItem value="specialty">Specialty</MenuItem>
          </TextField>

          {updateField === 'status' && (
            <TextField
              select
              fullWidth
              label="New Status"
              value={newStatus}
              onChange={(e) => setNewStatus(e.target.value)}
              helperText="All selected chapters will be updated to this status"
            >
              {STATUS_OPTIONS.map((status) => (
                <MenuItem key={status} value={status}>
                  {status.charAt(0).toUpperCase() + status.slice(1)}
                </MenuItem>
              ))}
            </TextField>
          )}

          {updateField === 'specialty' && (
            <TextField
              select
              fullWidth
              label="New Specialty"
              value={newSpecialty}
              onChange={(e) => setNewSpecialty(e.target.value)}
              helperText="All selected chapters will be updated to this specialty"
            >
              {SPECIALTIES.map((specialty) => (
                <MenuItem key={specialty} value={specialty}>
                  {specialty}
                </MenuItem>
              ))}
            </TextField>
          )}
        </DialogContent>
        <DialogActions>
          <Button onClick={() => setUpdateDialogOpen(false)} disabled={loading}>
            Cancel
          </Button>
          <Button
            onClick={handleUpdate}
            variant="contained"
            disabled={loading || (updateField === 'status' && !newStatus) || (updateField === 'specialty' && !newSpecialty)}
            startIcon={loading ? <></> : <CheckCircle />}
          >
            {loading ? 'Updating...' : 'Update All'}
          </Button>
        </DialogActions>
      </Dialog>
    </>
  )
}
