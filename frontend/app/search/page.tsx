'use client'

import { useState } from 'react'
import { Container, Typography, Box, TextField, Button, Paper } from '@mui/material'
import { Search as SearchIcon } from '@mui/icons-material'

export default function SearchPage() {
  const [query, setQuery] = useState('')

  const handleSearch = (e: React.FormEvent) => {
    e.preventDefault()
    // TODO: Implement search
    alert(`Searching for: ${query}`)
  }

  return (
    <Container maxWidth="lg" sx={{ py: 4 }}>
      <Box sx={{ mb: 4 }}>
        <Typography variant="h3" gutterBottom>
          <SearchIcon sx={{ verticalAlign: 'middle', mr: 1, fontSize: 40 }} />
          Search
        </Typography>
        <Typography variant="body1" color="text.secondary">
          Search across chapters, references, and procedures
        </Typography>
      </Box>

      <Paper sx={{ p: 3, mb: 4 }}>
        <form onSubmit={handleSearch}>
          <Box sx={{ display: 'flex', gap: 2 }}>
            <TextField
              fullWidth
              placeholder="Search neurosurgical topics..."
              value={query}
              onChange={(e) => setQuery(e.target.value)}
            />
            <Button
              type="submit"
              variant="contained"
              startIcon={<SearchIcon />}
            >
              Search
            </Button>
          </Box>
        </form>
      </Paper>

      <Box sx={{ textAlign: 'center', py: 8 }}>
        <Typography variant="body1" color="text.secondary">
          Enter a search query to get started
        </Typography>
      </Box>
    </Container>
  )
}
