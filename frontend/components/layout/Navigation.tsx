'use client'

import { useState } from 'react'
import Link from 'next/link'
import { 
  AppBar, 
  Toolbar, 
  Typography, 
  Button, 
  Box, 
  IconButton,
  Menu as MenuComponent,
  MenuItem,
  Divider,
  Chip,
} from '@mui/material'
import { 
  Psychology, 
  Menu as MenuIcon,
  AutoAwesome,
  PhotoLibrary,
  Search as SearchIcon,
  Science,
} from '@mui/icons-material'

export function Navigation() {
  const [anchorEl, setAnchorEl] = useState<null | HTMLElement>(null)
  const open = Boolean(anchorEl)

  const handleMenuClick = (event: React.MouseEvent<HTMLElement>) => {
    setAnchorEl(event.currentTarget)
  }

  const handleMenuClose = () => {
    setAnchorEl(null)
  }

  return (
    <AppBar position="sticky" sx={{ bgcolor: 'primary.main' }}>
      <Toolbar>
        <Psychology sx={{ mr: 2 }} />
        <Typography variant="h6" component="div" sx={{ flexGrow: 1 }}>
          NeuroKnowledge
          <Chip 
            label="v2.2" 
            size="small" 
            sx={{ ml: 1, height: 20, fontSize: '0.7rem' }}
            color="secondary"
          />
        </Typography>
        
        <Box sx={{ display: { xs: 'none', md: 'flex' }, gap: 1 }}>
          <Button color="inherit" component={Link} href="/">
            Home
          </Button>
          <Button color="inherit" component={Link} href="/library">
            Library
          </Button>
          <Button color="inherit" component={Link} href="/synthesis">
            Synthesis
          </Button>
          <Button 
            color="inherit" 
            component={Link} 
            href="/synthesis-comprehensive"
            startIcon={<AutoAwesome />}
          >
            Comprehensive
          </Button>
          <Button color="inherit" component={Link} href="/search">
            Search
          </Button>
          <Button 
            color="inherit" 
            component={Link} 
            href="/deep-search"
            startIcon={<SearchIcon />}
          >
            Deep Search
          </Button>
          <Button 
            color="inherit" 
            component={Link} 
            href="/image-tools"
            startIcon={<PhotoLibrary />}
          >
            Images
          </Button>
          <Button 
            color="inherit" 
            component={Link} 
            href="/alive-chapters"
            startIcon={<Science />}
          >
            Alive
          </Button>
          <Button color="inherit" component={Link} href="/references">
            References
          </Button>
          <Button color="inherit" component={Link} href="/qa">
            Q&A
          </Button>
        </Box>
        
        <IconButton
          color="inherit"
          sx={{ display: { md: 'none' } }}
          onClick={handleMenuClick}
        >
          <MenuIcon />
        </IconButton>

        <MenuComponent
          anchorEl={anchorEl}
          open={open}
          onClose={handleMenuClose}
        >
          <MenuItem component={Link} href="/" onClick={handleMenuClose}>
            Home
          </MenuItem>
          <MenuItem component={Link} href="/library" onClick={handleMenuClose}>
            Library
          </MenuItem>
          <Divider />
          <MenuItem component={Link} href="/synthesis" onClick={handleMenuClose}>
            Synthesis
          </MenuItem>
          <MenuItem component={Link} href="/synthesis-comprehensive" onClick={handleMenuClose}>
            Comprehensive Synthesis
          </MenuItem>
          <Divider />
          <MenuItem component={Link} href="/search" onClick={handleMenuClose}>
            Search
          </MenuItem>
          <MenuItem component={Link} href="/deep-search" onClick={handleMenuClose}>
            Deep Literature Search
          </MenuItem>
          <Divider />
          <MenuItem component={Link} href="/image-tools" onClick={handleMenuClose}>
            Image Tools
          </MenuItem>
          <MenuItem component={Link} href="/alive-chapters" onClick={handleMenuClose}>
            Alive Chapters
          </MenuItem>
          <Divider />
          <MenuItem component={Link} href="/references" onClick={handleMenuClose}>
            References
          </MenuItem>
          <MenuItem component={Link} href="/qa" onClick={handleMenuClose}>
            Q&A
          </MenuItem>
          <MenuItem component={Link} href="/settings" onClick={handleMenuClose}>
            Settings
          </MenuItem>
        </MenuComponent>
      </Toolbar>
    </AppBar>
  )
}
