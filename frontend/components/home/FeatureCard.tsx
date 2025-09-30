'use client'

import { Card, CardContent, Typography, Box, SvgIconProps } from '@mui/material'
import { ArrowForward } from '@mui/icons-material'
import Link from 'next/link'
import { motion } from 'framer-motion'

interface FeatureCardProps {
  title: string
  description: string
  icon: React.ComponentType<SvgIconProps>
  href: string
  color: 'primary' | 'secondary' | 'success' | 'info' | 'warning' | 'error'
}

export function FeatureCard({ title, description, icon: Icon, href, color }: FeatureCardProps) {
  return (
    <motion.div
      whileHover={{ scale: 1.02, y: -4 }}
      transition={{ type: 'spring', stiffness: 300 }}
    >
      <Card
        component={Link}
        href={href}
        sx={{
          height: '100%',
          display: 'flex',
          flexDirection: 'column',
          textDecoration: 'none',
          transition: 'all 0.3s',
          '&:hover': {
            boxShadow: 6,
          },
        }}
      >
        <CardContent sx={{ flexGrow: 1 }}>
          <Box
            sx={{
              display: 'flex',
              alignItems: 'center',
              justifyContent: 'center',
              width: 56,
              height: 56,
              borderRadius: '12px',
              bgcolor: `${color}.light`,
              mb: 2,
            }}
          >
            <Icon sx={{ fontSize: 32, color: `${color}.main` }} />
          </Box>
          
          <Typography variant="h6" component="h3" gutterBottom>
            {title}
          </Typography>
          
          <Typography variant="body2" color="text.secondary" paragraph>
            {description}
          </Typography>
          
          <Box
            sx={{
              display: 'flex',
              alignItems: 'center',
              color: `${color}.main`,
              mt: 'auto',
            }}
          >
            <Typography variant="button">Explore</Typography>
            <ArrowForward sx={{ ml: 0.5, fontSize: 20 }} />
          </Box>
        </CardContent>
      </Card>
    </motion.div>
  )
}
