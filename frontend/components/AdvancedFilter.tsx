import { useState } from 'react'
import {
  Box,
  TextField,
  MenuItem,
  Button,
  Accordion,
  AccordionSummary,
  AccordionDetails,
  Typography,
  Chip,
  Stack,
  Autocomplete,
} from '@mui/material'
import {
  ExpandMore,
  FilterList,
  Clear,
} from '@mui/icons-material'

const SPECIALTIES = [
  'All',
  'Neurosurgery General',
  'Brain Tumors',
  'Vascular Neurosurgery',
  'Spine Surgery',
  'Functional Neurosurgery',
  'Pediatric Neurosurgery',
  'Trauma',
  'Skull Base',
]

const STATUS_OPTIONS = ['all', 'published', 'draft', 'archived']

const SORT_OPTIONS = [
  { value: 'relevance', label: 'Relevance' },
  { value: 'date_desc', label: 'Newest First' },
  { value: 'date_asc', label: 'Oldest First' },
  { value: 'title_asc', label: 'Title (A-Z)' },
  { value: 'title_desc', label: 'Title (Z-A)' },
]

const SEARCH_FIELDS = [
  { value: 'all', label: 'All Fields' },
  { value: 'title', label: 'Title Only' },
  { value: 'content', label: 'Content Only' },
  { value: 'metadata', label: 'Metadata Only' },
]

export interface AdvancedFilterState {
  specialty: string
  status: string
  dateFrom: string
  dateTo: string
  tags: string[]
  searchField: string
  sortBy: string
}

interface AdvancedFilterProps {
  onApply: (filters: AdvancedFilterState) => void
  onReset: () => void
  initialFilters?: Partial<AdvancedFilterState>
}

const defaultFilters: AdvancedFilterState = {
  specialty: 'All',
  status: 'all',
  dateFrom: '',
  dateTo: '',
  tags: [],
  searchField: 'all',
  sortBy: 'relevance',
}

export default function AdvancedFilter({
  onApply,
  onReset,
  initialFilters = {},
}: AdvancedFilterProps) {
  const [filters, setFilters] = useState<AdvancedFilterState>({
    ...defaultFilters,
    ...initialFilters,
  })

  const [expanded, setExpanded] = useState(false)

  const handleApply = () => {
    onApply(filters)
    setExpanded(false)
  }

  const handleReset = () => {
    setFilters(defaultFilters)
    onReset()
    setExpanded(false)
  }

  const activeFilterCount = Object.entries(filters).filter(([key, value]) => {
    if (key === 'specialty') return value !== 'All'
    if (key === 'status') return value !== 'all'
    if (key === 'searchField') return value !== 'all'
    if (key === 'sortBy') return value !== 'relevance'
    if (key === 'tags') return Array.isArray(value) && value.length > 0
    if (key === 'dateFrom' || key === 'dateTo') return value !== ''
    return false
  }).length

  return (
    <Accordion
      expanded={expanded}
      onChange={(_, isExpanded) => setExpanded(isExpanded)}
      sx={{ mb: 3 }}
    >
      <AccordionSummary
        expandIcon={<ExpandMore />}
        sx={{
          backgroundColor: 'grey.50',
          '&:hover': { backgroundColor: 'grey.100' },
        }}
      >
        <Box sx={{ display: 'flex', alignItems: 'center', gap: 1, width: '100%' }}>
          <FilterList />
          <Typography>Advanced Filters</Typography>
          {activeFilterCount > 0 && (
            <Chip
              label={`${activeFilterCount} active`}
              size="small"
              color="primary"
              sx={{ ml: 'auto', mr: 2 }}
            />
          )}
        </Box>
      </AccordionSummary>

      <AccordionDetails>
        <Stack spacing={3}>
          {/* Row 1: Specialty and Status */}
          <Box sx={{ display: 'flex', gap: 2 }}>
            <TextField
              select
              label="Specialty"
              value={filters.specialty}
              onChange={(e) => setFilters({ ...filters, specialty: e.target.value })}
              sx={{ flex: 1 }}
              size="small"
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
              value={filters.status}
              onChange={(e) => setFilters({ ...filters, status: e.target.value })}
              sx={{ flex: 1 }}
              size="small"
            >
              {STATUS_OPTIONS.map((status) => (
                <MenuItem key={status} value={status}>
                  {status.charAt(0).toUpperCase() + status.slice(1)}
                </MenuItem>
              ))}
            </TextField>
          </Box>

          {/* Row 2: Date Range */}
          <Box sx={{ display: 'flex', gap: 2 }}>
            <TextField
              label="Date From"
              type="date"
              value={filters.dateFrom}
              onChange={(e) => setFilters({ ...filters, dateFrom: e.target.value })}
              sx={{ flex: 1 }}
              size="small"
              InputLabelProps={{ shrink: true }}
            />

            <TextField
              label="Date To"
              type="date"
              value={filters.dateTo}
              onChange={(e) => setFilters({ ...filters, dateTo: e.target.value })}
              sx={{ flex: 1 }}
              size="small"
              InputLabelProps={{ shrink: true }}
            />
          </Box>

          {/* Row 3: Tags */}
          <Autocomplete
            multiple
            freeSolo
            options={[]}
            value={filters.tags}
            onChange={(_, newValue) => setFilters({ ...filters, tags: newValue })}
            renderInput={(params) => (
              <TextField
                {...params}
                label="Tags"
                placeholder="Type and press Enter to add tags"
                size="small"
              />
            )}
            renderTags={(value, getTagProps) =>
              value.map((option, index) => (
                <Chip
                  label={option}
                  size="small"
                  {...getTagProps({ index })}
                  key={option}
                />
              ))
            }
          />

          {/* Row 4: Search Field and Sort */}
          <Box sx={{ display: 'flex', gap: 2 }}>
            <TextField
              select
              label="Search In"
              value={filters.searchField}
              onChange={(e) => setFilters({ ...filters, searchField: e.target.value })}
              sx={{ flex: 1 }}
              size="small"
            >
              {SEARCH_FIELDS.map((field) => (
                <MenuItem key={field.value} value={field.value}>
                  {field.label}
                </MenuItem>
              ))}
            </TextField>

            <TextField
              select
              label="Sort By"
              value={filters.sortBy}
              onChange={(e) => setFilters({ ...filters, sortBy: e.target.value })}
              sx={{ flex: 1 }}
              size="small"
            >
              {SORT_OPTIONS.map((option) => (
                <MenuItem key={option.value} value={option.value}>
                  {option.label}
                </MenuItem>
              ))}
            </TextField>
          </Box>

          {/* Action Buttons */}
          <Box sx={{ display: 'flex', gap: 2, justifyContent: 'flex-end' }}>
            <Button
              variant="outlined"
              startIcon={<Clear />}
              onClick={handleReset}
              disabled={activeFilterCount === 0}
            >
              Clear Filters
            </Button>
            <Button
              variant="contained"
              startIcon={<FilterList />}
              onClick={handleApply}
            >
              Apply Filters
            </Button>
          </Box>
        </Stack>
      </AccordionDetails>
    </Accordion>
  )
}
