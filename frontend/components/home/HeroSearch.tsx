'use client'

import { useState } from 'react'
import { TextField, IconButton, Paper, InputAdornment } from '@mui/material'
import { Search } from '@mui/icons-material'

interface HeroSearchProps {
  onSearch: (query: string) => void
}

export function HeroSearch({ onSearch }: HeroSearchProps) {
  const [query, setQuery] = useState('')

  const handleSubmit = (e: React.FormEvent) => {
    e.preventDefault()
    if (query.trim()) {
      onSearch(query)
    }
  }

  return (
    <Paper
      component="form"
      onSubmit={handleSubmit}
      sx={{
        maxWidth: 600,
        mx: 'auto',
        p: '4px 8px',
        display: 'flex',
        alignItems: 'center',
        bgcolor: 'rgba(255, 255, 255, 0.95)',
        backdropFilter: 'blur(10px)',
      }}
      elevation={3}
    >
      <TextField
        fullWidth
        placeholder="Search neurosurgical topics, procedures, or guidelines..."
        value={query}
        onChange={(e) => setQuery(e.target.value)}
        variant="standard"
        InputProps={{
          disableUnderline: true,
          startAdornment: (
            <InputAdornment position="start">
              <Search color="action" />
            </InputAdornment>
          ),
        }}
        sx={{ ml: 1, flex: 1 }}
      />
      <IconButton type="submit" sx={{ p: '10px' }} aria-label="search">
        <Search />
      </IconButton>
    </Paper>
  )
}
