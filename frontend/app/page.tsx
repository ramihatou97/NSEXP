'use client'

import { useState } from 'react'
import { motion } from 'framer-motion'
import {
  Psychology as Brain,
  Search,
  MenuBook as BookOpen,
  AutoAwesome,
  Science,
  LocalHospital,
  Timeline,
  Psychology,
  Biotech,
  MedicalServices,
} from '@mui/icons-material'
import { Button, Card, CardContent, Typography, Grid, Container, Box, Chip } from '@mui/material'
import Link from 'next/link'
import { useRouter } from 'next/navigation'
import { HeroSearch } from '@/components/home/HeroSearch'
import { FeatureCard } from '@/components/home/FeatureCard'
import { StatisticsSection } from '@/components/home/StatisticsSection'
import { RecentChapters } from '@/components/home/RecentChapters'

const neurosurgicalSpecialties = [
  { name: 'Brain Tumors', icon: Brain, color: '#e91e63' },
  { name: 'Vascular', icon: Timeline, color: '#f44336' },
  { name: 'Spine', icon: MedicalServices, color: '#ff9800' },
  { name: 'Functional', icon: Psychology, color: '#4caf50' },
  { name: 'Pediatric', icon: LocalHospital, color: '#2196f3' },
  { name: 'Skull Base', icon: Biotech, color: '#9c27b0' },
]

const features = [
  {
    title: 'Comprehensive Synthesis',
    description: 'Generate chapters with 150+ sections covering all aspects of neurosurgical topics - NEW in v2.2!',
    icon: AutoAwesome,
    href: '/synthesis-comprehensive',
    color: 'primary',
    badge: 'NEW',
  },
  {
    title: 'Deep Literature Search',
    description: 'Search PubMed, arXiv with intelligent deduplication and relevance scoring - NEW in v2.2!',
    icon: Search,
    href: '/deep-search',
    color: 'secondary',
    badge: 'NEW',
  },
  {
    title: 'Image Extraction & OCR',
    description: 'Extract and analyze medical images from PDFs with dual OCR engines - NEW in v2.2!',
    icon: BookOpen,
    href: '/image-tools',
    color: 'success',
    badge: 'NEW',
  },
  {
    title: 'Alive Chapters',
    description: 'Interactive chapters with Q&A, citations, and behavioral learning - NEW in v2.2!',
    icon: Science,
    href: '/alive-chapters',
    color: 'info',
    badge: 'NEW',
  },
  {
    title: 'Basic Synthesis',
    description: 'Quick chapter generation with AI-powered content synthesis',
    icon: AutoAwesome,
    href: '/synthesis',
    color: 'warning',
  },
  {
    title: 'Q&A Assistant',
    description: 'Get instant answers with clinical context and evidence-based references',
    icon: Psychology,
    href: '/qa',
    color: 'error',
  },
  {
    title: 'Chapter Library',
    description: 'Access and manage your neurosurgical knowledge base with version control',
    icon: MedicalServices,
    href: '/library',
    color: 'primary',
  },
  {
    title: 'Clinical Tools',
    description: 'Access surgical planning, neuronavigation, and decision support tools',
    icon: MedicalServices,
    href: '/tools',
    color: 'secondary',
  },
]

export default function HomePage() {
  const router = useRouter()
  const [searchQuery, setSearchQuery] = useState('')

  const handleSearch = (query: string) => {
    setSearchQuery(query)
    router.push(`/search?q=${encodeURIComponent(query)}`)
  }

  return (
    <div className="min-h-screen">
      {/* Hero Section */}
      <section className="relative overflow-hidden bg-gradient-to-br from-blue-600 via-blue-700 to-blue-800 pb-20 pt-32">
        <div className="absolute inset-0 bg-black/10" />

        {/* Animated Brain Background */}
        <div className="absolute inset-0 opacity-10">
          <div className="animate-pulse-slow absolute left-1/4 top-1/4 h-96 w-96 rounded-full bg-white/20 blur-3xl" />
          <div className="animate-pulse-slow absolute bottom-1/4 right-1/4 h-96 w-96 rounded-full bg-white/20 blur-3xl delay-1000" />
        </div>

        <Container maxWidth="lg" className="relative z-10">
          <motion.div
            initial={{ opacity: 0, y: 20 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ duration: 0.6 }}
            className="text-center text-white"
          >
            <Brain className="mx-auto mb-6 h-20 w-20" />

            <Typography variant="h1" className="mb-4 font-bold">
              Neurosurgical Knowledge
              <span className="block text-blue-200">Management System</span>
            </Typography>

            <Typography variant="h5" className="mb-8 text-blue-100">
              Advanced AI-powered platform for neurosurgical education, research, and clinical practice
            </Typography>

            <HeroSearch onSearch={handleSearch} />

            {/* Specialty Chips */}
            <div className="mt-8 flex flex-wrap justify-center gap-2">
              {neurosurgicalSpecialties.map((specialty) => (
                <Chip
                  key={specialty.name}
                  label={specialty.name}
                  icon={<specialty.icon />}
                  onClick={() => handleSearch(specialty.name)}
                  className="cursor-pointer bg-white/20 text-white hover:bg-white/30"
                  style={{ borderColor: specialty.color }}
                />
              ))}
            </div>
          </motion.div>
        </Container>
      </section>

      {/* Features Section */}
      <section className="py-16">
        <Container maxWidth="lg">
          <motion.div
            initial={{ opacity: 0 }}
            animate={{ opacity: 1 }}
            transition={{ duration: 0.6, delay: 0.2 }}
          >
            <Typography variant="h2" className="mb-2 text-center font-bold">
              Comprehensive Neurosurgical Tools
            </Typography>
            <Typography variant="body1" className="mb-12 text-center text-gray-600">
              Everything you need for neurosurgical knowledge management and clinical excellence
            </Typography>

            <Grid container spacing={4}>
              {features.map((feature, index) => (
                <Grid item xs={12} md={6} lg={4} key={feature.title}>
                  <motion.div
                    initial={{ opacity: 0, y: 20 }}
                    animate={{ opacity: 1, y: 0 }}
                    transition={{ duration: 0.6, delay: 0.1 * index }}
                  >
                    <FeatureCard {...feature} />
                  </motion.div>
                </Grid>
              ))}
            </Grid>
          </motion.div>
        </Container>
      </section>

      {/* Statistics Section */}
      <section className="bg-gray-100 py-16">
        <Container maxWidth="lg">
          <StatisticsSection />
        </Container>
      </section>

      {/* Recent Chapters Section */}
      <section className="py-16">
        <Container maxWidth="lg">
          <Typography variant="h3" className="mb-8 text-center font-bold">
            Recent Chapters
          </Typography>
          <RecentChapters />
        </Container>
      </section>

      {/* CTA Section */}
      <section className="bg-gradient-to-r from-blue-600 to-blue-700 py-16 text-white">
        <Container maxWidth="md">
          <motion.div
            initial={{ opacity: 0, scale: 0.95 }}
            animate={{ opacity: 1, scale: 1 }}
            transition={{ duration: 0.6 }}
            className="text-center"
          >
            <Typography variant="h3" className="mb-4 font-bold">
              Ready to Transform Your Neurosurgical Practice?
            </Typography>
            <Typography variant="h6" className="mb-8 text-blue-100">
              Join thousands of neurosurgeons advancing their knowledge with AI
            </Typography>

            <div className="flex justify-center gap-4">
              <Button
                component={Link}
                href="/library"
                variant="contained"
                size="large"
                className="bg-white text-blue-600 hover:bg-blue-50"
              >
                Browse Library
              </Button>
              <Button
                component={Link}
                href="/synthesis"
                variant="outlined"
                size="large"
                className="border-white text-white hover:bg-white/10"
              >
                Start Synthesis
              </Button>
            </div>
          </motion.div>
        </Container>
      </section>
    </div>
  )
}