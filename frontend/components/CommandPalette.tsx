'use client'

import { useState, useEffect, useCallback } from 'react'
import { useRouter } from 'next/navigation'
import {
  Dialog,
  DialogContent,
  TextField,
  List,
  ListItem,
  ListItemButton,
  ListItemIcon,
  ListItemText,
  Typography,
  Box,
  Chip,
} from '@mui/material'
import {
  Search,
  LibraryBooks,
  AutoAwesome,
  QuestionAnswer,
  Settings,
  Home,
} from '@mui/icons-material'

interface Command {
  id: string
  label: string
  description: string
  icon: React.ReactNode
  action: () => void
  keywords: string[]
}

interface CommandPaletteProps {
  open: boolean
  onClose: () => void
}

export function CommandPalette({ open, onClose }: CommandPaletteProps) {
  const router = useRouter()
  const [search, setSearch] = useState('')
  const [filteredCommands, setFilteredCommands] = useState<Command[]>([])

  const commands: Command[] = [
    {
      id: 'home',
      label: 'Go to Home',
      description: 'Navigate to home page',
      icon: <Home />,
      action: () => router.push('/'),
      keywords: ['home', 'dashboard', 'main'],
    },
    {
      id: 'library',
      label: 'Browse Library',
      description: 'View all chapters in your library',
      icon: <LibraryBooks />,
      action: () => router.push('/library'),
      keywords: ['library', 'chapters', 'books', 'browse'],
    },
    {
      id: 'search',
      label: 'Search',
      description: 'Search through your knowledge base',
      icon: <Search />,
      action: () => router.push('/search'),
      keywords: ['search', 'find', 'query'],
    },
    {
      id: 'synthesis',
      label: 'Generate Synthesis',
      description: 'Create new chapter from references',
      icon: <AutoAwesome />,
      action: () => router.push('/synthesis'),
      keywords: ['synthesis', 'generate', 'create', 'ai'],
    },
    {
      id: 'qa',
      label: 'Q&A System',
      description: 'Ask questions about your chapters',
      icon: <QuestionAnswer />,
      action: () => router.push('/qa'),
      keywords: ['qa', 'questions', 'ask', 'answers'],
    },
  ]

  useEffect(() => {
    if (!search.trim()) {
      setFilteredCommands(commands)
      return
    }

    const searchLower = search.toLowerCase()
    const filtered = commands.filter(
      (cmd) =>
        cmd.label.toLowerCase().includes(searchLower) ||
        cmd.description.toLowerCase().includes(searchLower) ||
        cmd.keywords.some((k) => k.includes(searchLower))
    )
    setFilteredCommands(filtered)
  }, [search])

  const handleCommandSelect = useCallback(
    (command: Command) => {
      command.action()
      onClose()
      setSearch('')
    },
    [onClose]
  )

  const handleClose = useCallback(() => {
    onClose()
    setSearch('')
  }, [onClose])

  return (
    <Dialog
      open={open}
      onClose={handleClose}
      maxWidth="sm"
      fullWidth
      PaperProps={{
        sx: {
          position: 'fixed',
          top: 100,
          m: 0,
        },
      }}
    >
      <DialogContent sx={{ p: 0 }}>
        <Box sx={{ p: 2, borderBottom: 1, borderColor: 'divider' }}>
          <TextField
            fullWidth
            autoFocus
            placeholder="Type a command or search..."
            value={search}
            onChange={(e) => setSearch(e.target.value)}
            variant="outlined"
            size="small"
            InputProps={{
              startAdornment: <Search sx={{ mr: 1, color: 'text.secondary' }} />,
            }}
          />
        </Box>

        <List sx={{ maxHeight: 400, overflow: 'auto', p: 1 }}>
          {filteredCommands.length === 0 ? (
            <Box sx={{ p: 4, textAlign: 'center' }}>
              <Typography variant="body2" color="text.secondary">
                No commands found
              </Typography>
            </Box>
          ) : (
            filteredCommands.map((command) => (
              <ListItem key={command.id} disablePadding sx={{ mb: 0.5 }}>
                <ListItemButton
                  onClick={() => handleCommandSelect(command)}
                  sx={{
                    borderRadius: 1,
                    '&:hover': {
                      backgroundColor: 'action.hover',
                    },
                  }}
                >
                  <ListItemIcon sx={{ minWidth: 40 }}>{command.icon}</ListItemIcon>
                  <ListItemText
                    primary={command.label}
                    secondary={command.description}
                    primaryTypographyProps={{
                      variant: 'body2',
                      fontWeight: 500,
                    }}
                    secondaryTypographyProps={{
                      variant: 'caption',
                    }}
                  />
                  <Chip
                    label="↵"
                    size="small"
                    sx={{
                      ml: 1,
                      height: 20,
                      fontSize: '0.75rem',
                    }}
                  />
                </ListItemButton>
              </ListItem>
            ))
          )}
        </List>

        <Box
          sx={{
            p: 1.5,
            borderTop: 1,
            borderColor: 'divider',
            display: 'flex',
            gap: 1,
            justifyContent: 'center',
          }}
        >
          <Chip label="⌘K" size="small" variant="outlined" />
          <Typography variant="caption" color="text.secondary">
            to open
          </Typography>
          <Chip label="ESC" size="small" variant="outlined" />
          <Typography variant="caption" color="text.secondary">
            to close
          </Typography>
        </Box>
      </DialogContent>
    </Dialog>
  )
}

export default CommandPalette
