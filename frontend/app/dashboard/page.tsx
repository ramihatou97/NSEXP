'use client'

import { Container, Typography, Box, Alert, Button, CircularProgress } from '@mui/material'
import { Dashboard as DashboardIcon, Refresh } from '@mui/icons-material'
import dynamic from 'next/dynamic'
import { useState, useEffect } from 'react'

// Code splitting: Lazy load heavy dashboard component
const UserActivityDashboard = dynamic(() => import('@/components/UserActivityDashboard'), {
  loading: () => <Box sx={{ display: 'flex', justifyContent: 'center', py: 8 }}><CircularProgress /></Box>,
  ssr: false
})

export default function DashboardPage() {
  const [data, setData] = useState(null)
  const [loading, setLoading] = useState(false)
  const [error, setError] = useState<string | null>(null)

  const fetchDashboardData = async () => {
    setLoading(true)
    setError(null)
    try {
      const response = await fetch(
        `${process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000/api/v1'}/analytics/dashboard`
      )

      if (!response.ok) {
        // If API not available, use mock data
        if (response.status === 404) {
          setData(null) // Will use mock data in component
          return
        }
        throw new Error('Failed to fetch dashboard data')
      }

      const result = await response.json()
      setData(result)
    } catch (err: any) {
      // Silently fail and use mock data
      setData(null)
    } finally {
      setLoading(false)
    }
  }

  useEffect(() => {
    fetchDashboardData()
  }, [])

  return (
    <Container maxWidth="xl" sx={{ py: 4 }}>
      {/* Header */}
      <Box sx={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', mb: 4 }}>
        <Box>
          <Typography variant="h3" gutterBottom>
            <DashboardIcon sx={{ verticalAlign: 'middle', mr: 1, fontSize: 40 }} />
            Dashboard
          </Typography>
          <Typography variant="body1" color="text.secondary">
            Overview of your activity and popular content
          </Typography>
        </Box>
        <Button
          variant="outlined"
          startIcon={loading ? <CircularProgress size={20} /> : <Refresh />}
          onClick={fetchDashboardData}
          disabled={loading}
        >
          Refresh
        </Button>
      </Box>

      {/* Info Alert (if using mock data) */}
      {!data && !loading && (
        <Alert severity="info" sx={{ mb: 3 }}>
          Displaying sample data. Connect to the backend API for real-time statistics.
        </Alert>
      )}

      {/* Error State */}
      {error && (
        <Alert severity="error" sx={{ mb: 3 }} onClose={() => setError(null)}>
          {error}
        </Alert>
      )}

      {/* Loading State */}
      {loading && (
        <Box sx={{ display: 'flex', justifyContent: 'center', py: 8 }}>
          <CircularProgress size={60} />
        </Box>
      )}

      {/* Dashboard Content */}
      {!loading && <UserActivityDashboard data={data || undefined} />}
    </Container>
  )
}
