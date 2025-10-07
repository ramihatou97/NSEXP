import {
  Box,
  Card,
  CardContent,
  Grid,
  Typography,
  LinearProgress,
  Chip,
  List,
  ListItem,
  ListItemText,
  ListItemIcon,
  Avatar,
  Paper,
  Divider,
} from '@mui/material'
import {
  TrendingUp,
  MenuBook,
  Search,
  Edit,
  Visibility,
  AccessTime,
  CheckCircle,
} from '@mui/icons-material'

interface MetricCardProps {
  title: string
  value: string | number
  change?: string
  icon: React.ReactNode
  color: string
}

function MetricCard({ title, value, change, icon, color }: MetricCardProps) {
  const isPositive = change && change.startsWith('+')

  return (
    <Card sx={{ height: '100%' }}>
      <CardContent>
        <Box sx={{ display: 'flex', alignItems: 'center', mb: 2 }}>
          <Avatar sx={{ bgcolor: `${color}.light`, color: `${color}.main`, mr: 2 }}>
            {icon}
          </Avatar>
          <Box sx={{ flex: 1 }}>
            <Typography variant="body2" color="text.secondary">
              {title}
            </Typography>
            <Typography variant="h4" sx={{ fontWeight: 600 }}>
              {value}
            </Typography>
          </Box>
        </Box>
        {change && (
          <Chip
            label={change}
            size="small"
            color={isPositive ? 'success' : 'error'}
            sx={{ fontWeight: 600 }}
          />
        )}
      </CardContent>
    </Card>
  )
}

interface Activity {
  id: string
  type: 'create' | 'edit' | 'view' | 'search'
  title: string
  timestamp: string
  details?: string
}

interface DashboardData {
  metrics: {
    totalChapters: number
    chaptersChange: string
    recentSearches: number
    searchesChange: string
    totalViews: number
    viewsChange: string
    activeToday: number
    activeTodayChange: string
  }
  recentActivity: Activity[]
  popularContent: Array<{
    id: string
    title: string
    views: number
    specialty: string
  }>
  activityByHour: number[]
}

interface UserActivityDashboardProps {
  data?: DashboardData
}

// Mock data for initial display
const mockData: DashboardData = {
  metrics: {
    totalChapters: 47,
    chaptersChange: '+3 this week',
    recentSearches: 124,
    searchesChange: '+12%',
    totalViews: 1834,
    viewsChange: '+24%',
    activeToday: 8,
    activeTodayChange: '+2',
  },
  recentActivity: [
    {
      id: '1',
      type: 'create',
      title: 'Created chapter on Glioblastoma Treatment',
      timestamp: '2 hours ago',
      details: 'Brain Tumors',
    },
    {
      id: '2',
      type: 'edit',
      title: 'Updated Aneurysm Clipping Protocol',
      timestamp: '4 hours ago',
      details: 'Vascular Neurosurgery',
    },
    {
      id: '3',
      type: 'search',
      title: 'Searched for "spinal fusion techniques"',
      timestamp: '5 hours ago',
    },
    {
      id: '4',
      type: 'view',
      title: 'Viewed Craniotomy Procedures',
      timestamp: '6 hours ago',
      details: 'Skull Base',
    },
    {
      id: '5',
      type: 'create',
      title: 'Created chapter on Pediatric Hydrocephalus',
      timestamp: 'Yesterday',
      details: 'Pediatric Neurosurgery',
    },
  ],
  popularContent: [
    {
      id: '1',
      title: 'Craniotomy: Standard Approaches',
      views: 234,
      specialty: 'Neurosurgery General',
    },
    {
      id: '2',
      title: 'Glioblastoma: Current Treatment Paradigm',
      views: 189,
      specialty: 'Brain Tumors',
    },
    {
      id: '3',
      title: 'Aneurysm Clipping vs Coiling',
      views: 156,
      specialty: 'Vascular Neurosurgery',
    },
    {
      id: '4',
      title: 'Spinal Fusion Techniques',
      views: 143,
      specialty: 'Spine Surgery',
    },
  ],
  activityByHour: [2, 1, 0, 0, 1, 3, 5, 8, 12, 15, 18, 22, 20, 16, 14, 18, 22, 19, 15, 10, 7, 5, 4, 3],
}

export default function UserActivityDashboard({ data = mockData }: UserActivityDashboardProps) {
  const getActivityIcon = (type: Activity['type']) => {
    switch (type) {
      case 'create':
        return <MenuBook color="primary" />
      case 'edit':
        return <Edit color="warning" />
      case 'view':
        return <Visibility color="info" />
      case 'search':
        return <Search color="secondary" />
    }
  }

  const getActivityColor = (type: Activity['type']) => {
    switch (type) {
      case 'create':
        return 'primary.light'
      case 'edit':
        return 'warning.light'
      case 'view':
        return 'info.light'
      case 'search':
        return 'secondary.light'
    }
  }

  const maxViews = Math.max(...data.popularContent.map(c => c.views))

  return (
    <Box>
      {/* Key Metrics */}
      <Grid container spacing={3} sx={{ mb: 4 }}>
        <Grid item xs={12} sm={6} md={3}>
          <MetricCard
            title="Total Chapters"
            value={data.metrics.totalChapters}
            change={data.metrics.chaptersChange}
            icon={<MenuBook />}
            color="primary"
          />
        </Grid>
        <Grid item xs={12} sm={6} md={3}>
          <MetricCard
            title="Recent Searches"
            value={data.metrics.recentSearches}
            change={data.metrics.searchesChange}
            icon={<Search />}
            color="secondary"
          />
        </Grid>
        <Grid item xs={12} sm={6} md={3}>
          <MetricCard
            title="Total Views"
            value={data.metrics.totalViews}
            change={data.metrics.viewsChange}
            icon={<Visibility />}
            color="info"
          />
        </Grid>
        <Grid item xs={12} sm={6} md={3}>
          <MetricCard
            title="Active Today"
            value={data.metrics.activeToday}
            change={data.metrics.activeTodayChange}
            icon={<TrendingUp />}
            color="success"
          />
        </Grid>
      </Grid>

      <Grid container spacing={3}>
        {/* Recent Activity */}
        <Grid item xs={12} lg={6}>
          <Card>
            <CardContent>
              <Typography variant="h6" gutterBottom sx={{ display: 'flex', alignItems: 'center', gap: 1 }}>
                <AccessTime />
                Recent Activity
              </Typography>
              <Divider sx={{ my: 2 }} />
              <List>
                {data.recentActivity.map((activity, index) => (
                  <ListItem
                    key={activity.id}
                    sx={{
                      borderRadius: 1,
                      mb: 1,
                      bgcolor: index === 0 ? getActivityColor(activity.type) : 'transparent',
                    }}
                  >
                    <ListItemIcon>{getActivityIcon(activity.type)}</ListItemIcon>
                    <ListItemText
                      primary={activity.title}
                      secondary={
                        <Box sx={{ display: 'flex', alignItems: 'center', gap: 1, mt: 0.5 }}>
                          <Typography variant="caption" color="text.secondary">
                            {activity.timestamp}
                          </Typography>
                          {activity.details && (
                            <Chip label={activity.details} size="small" variant="outlined" />
                          )}
                        </Box>
                      }
                    />
                  </ListItem>
                ))}
              </List>
            </CardContent>
          </Card>
        </Grid>

        {/* Popular Content */}
        <Grid item xs={12} lg={6}>
          <Card>
            <CardContent>
              <Typography variant="h6" gutterBottom sx={{ display: 'flex', alignItems: 'center', gap: 1 }}>
                <TrendingUp />
                Popular Content
              </Typography>
              <Divider sx={{ my: 2 }} />
              <List>
                {data.popularContent.map((content, index) => (
                  <ListItem key={content.id} sx={{ mb: 2 }}>
                    <Box sx={{ width: '100%' }}>
                      <Box sx={{ display: 'flex', justifyContent: 'space-between', mb: 1 }}>
                        <Typography variant="body2" sx={{ fontWeight: 500 }}>
                          {content.title}
                        </Typography>
                        <Chip
                          label={`${content.views} views`}
                          size="small"
                          color={index === 0 ? 'primary' : 'default'}
                        />
                      </Box>
                      <Chip label={content.specialty} size="small" variant="outlined" sx={{ mb: 1 }} />
                      <LinearProgress
                        variant="determinate"
                        value={(content.views / maxViews) * 100}
                        sx={{ height: 6, borderRadius: 1 }}
                      />
                    </Box>
                  </ListItem>
                ))}
              </List>
            </CardContent>
          </Card>
        </Grid>

        {/* Activity Heatmap */}
        <Grid item xs={12}>
          <Card>
            <CardContent>
              <Typography variant="h6" gutterBottom>
                Activity by Hour (Today)
              </Typography>
              <Divider sx={{ my: 2 }} />
              <Box sx={{ display: 'flex', alignItems: 'flex-end', gap: 0.5, height: 120 }}>
                {data.activityByHour.map((count, hour) => {
                  const maxActivity = Math.max(...data.activityByHour)
                  const height = maxActivity > 0 ? (count / maxActivity) * 100 : 0

                  return (
                    <Box
                      key={hour}
                      sx={{
                        flex: 1,
                        height: `${height}%`,
                        bgcolor: count > 0 ? 'primary.main' : 'grey.200',
                        borderRadius: 0.5,
                        minHeight: count > 0 ? 4 : 2,
                        transition: 'all 0.3s',
                        '&:hover': {
                          bgcolor: 'primary.dark',
                          transform: 'scaleY(1.1)',
                        },
                        cursor: 'pointer',
                      }}
                      title={`${hour}:00 - ${count} activities`}
                    />
                  )
                })}
              </Box>
              <Box sx={{ display: 'flex', justifyContent: 'space-between', mt: 1 }}>
                <Typography variant="caption" color="text.secondary">
                  00:00
                </Typography>
                <Typography variant="caption" color="text.secondary">
                  12:00
                </Typography>
                <Typography variant="caption" color="text.secondary">
                  23:00
                </Typography>
              </Box>
            </CardContent>
          </Card>
        </Grid>
      </Grid>
    </Box>
  )
}
