'use client'

import { Box, CircularProgress, Skeleton, Typography } from '@mui/material'

/**
 * Page-level loader with full-page spinner
 */
export function PageLoader() {
  return (
    <Box
      sx={{
        display: 'flex',
        justifyContent: 'center',
        alignItems: 'center',
        minHeight: '60vh',
        flexDirection: 'column',
        gap: 2,
      }}
    >
      <CircularProgress size={60} />
      <Typography variant="body2" color="text.secondary">
        Loading...
      </Typography>
    </Box>
  )
}

/**
 * List loader with skeleton cards
 */
export function ListLoader({ count = 3 }: { count?: number }) {
  return (
    <Box sx={{ display: 'flex', flexDirection: 'column', gap: 2 }}>
      {Array.from({ length: count }).map((_, index) => (
        <Box
          key={index}
          sx={{
            p: 3,
            border: 1,
            borderColor: 'divider',
            borderRadius: 2,
          }}
        >
          <Skeleton variant="text" width="60%" height={32} />
          <Skeleton variant="text" width="40%" height={24} sx={{ mt: 1 }} />
          <Skeleton variant="rectangular" width="100%" height={80} sx={{ mt: 2 }} />
          <Box sx={{ display: 'flex', gap: 1, mt: 2 }}>
            <Skeleton variant="rounded" width={80} height={32} />
            <Skeleton variant="rounded" width={80} height={32} />
          </Box>
        </Box>
      ))}
    </Box>
  )
}

/**
 * Card loader for grid layouts
 */
export function CardLoader({ count = 4 }: { count?: number }) {
  return (
    <Box
      sx={{
        display: 'grid',
        gridTemplateColumns: {
          xs: '1fr',
          sm: 'repeat(2, 1fr)',
          md: 'repeat(3, 1fr)',
        },
        gap: 3,
      }}
    >
      {Array.from({ length: count }).map((_, index) => (
        <Box
          key={index}
          sx={{
            p: 2,
            border: 1,
            borderColor: 'divider',
            borderRadius: 2,
          }}
        >
          <Skeleton variant="rectangular" width="100%" height={180} />
          <Skeleton variant="text" width="80%" height={28} sx={{ mt: 2 }} />
          <Skeleton variant="text" width="60%" height={20} sx={{ mt: 1 }} />
        </Box>
      ))}
    </Box>
  )
}

/**
 * Table loader with skeleton rows
 */
export function TableLoader({ rows = 5 }: { rows?: number }) {
  return (
    <Box sx={{ display: 'flex', flexDirection: 'column', gap: 1 }}>
      {/* Header */}
      <Box sx={{ display: 'flex', gap: 2, pb: 2, borderBottom: 2, borderColor: 'divider' }}>
        <Skeleton variant="text" width="30%" height={24} />
        <Skeleton variant="text" width="20%" height={24} />
        <Skeleton variant="text" width="20%" height={24} />
        <Skeleton variant="text" width="15%" height={24} />
        <Skeleton variant="text" width="15%" height={24} />
      </Box>
      {/* Rows */}
      {Array.from({ length: rows }).map((_, index) => (
        <Box key={index} sx={{ display: 'flex', gap: 2, py: 1.5, borderBottom: 1, borderColor: 'divider' }}>
          <Skeleton variant="text" width="30%" height={20} />
          <Skeleton variant="text" width="20%" height={20} />
          <Skeleton variant="text" width="20%" height={20} />
          <Skeleton variant="text" width="15%" height={20} />
          <Skeleton variant="rectangular" width="15%" height={24} />
        </Box>
      ))}
    </Box>
  )
}

/**
 * Content loader for text-heavy pages
 */
export function ContentLoader() {
  return (
    <Box>
      <Skeleton variant="text" width="70%" height={48} />
      <Skeleton variant="text" width="40%" height={28} sx={{ mt: 1 }} />
      <Box sx={{ mt: 4 }}>
        <Skeleton variant="rectangular" width="100%" height={200} />
        <Skeleton variant="text" width="100%" height={20} sx={{ mt: 2 }} />
        <Skeleton variant="text" width="100%" height={20} />
        <Skeleton variant="text" width="90%" height={20} />
        <Skeleton variant="text" width="95%" height={20} />
      </Box>
      <Box sx={{ mt: 4 }}>
        <Skeleton variant="rectangular" width="100%" height={150} />
        <Skeleton variant="text" width="100%" height={20} sx={{ mt: 2 }} />
        <Skeleton variant="text" width="100%" height={20} />
        <Skeleton variant="text" width="85%" height={20} />
      </Box>
    </Box>
  )
}

/**
 * Inline loader for buttons/small components
 */
export function InlineLoader({ size = 20 }: { size?: number }) {
  return <CircularProgress size={size} thickness={4} />
}
