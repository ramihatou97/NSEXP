'use client'

import Link from 'next/link'
import { AppBar, Toolbar, Typography, Button, Box, IconButton } from '@mui/material'
import { Brain, Menu } from '@mui/icons-material'

export function Navigation() {
  return (
    <AppBar position="sticky" sx={{ bgcolor: 'primary.main' }}>
      <Toolbar>
        <Brain sx={{ mr: 2 }} />
        <Typography variant="h6" component="div" sx={{ flexGrow: 1 }}>
          NeuroKnowledge
        </Typography>
        
        <Box sx={{ display: { xs: 'none', md: 'flex' }, gap: 2 }}>
          <Button color="inherit" component={Link} href="/">
            Home
          </Button>
          <Button color="inherit" component={Link} href="/library">
            Library
          </Button>
          <Button color="inherit" component={Link} href="/synthesis">
            Synthesis
          </Button>
          <Button color="inherit" component={Link} href="/search">
            Search
          </Button>
          <Button color="inherit" component={Link} href="/qa">
            Q&A
          </Button>
        </Box>
        
        <IconButton
          color="inherit"
          sx={{ display: { md: 'none' } }}
        >
          <Menu />
        </IconButton>
      </Toolbar>
    </AppBar>
  )
}
