/**
 * Shared TypeScript type definitions
 */

// Chapter types
export interface Chapter {
  id: string
  title: string
  specialty: string
  status: 'draft' | 'published' | 'archived'
  content: any
  metadata?: any
  version: number
  created_at: string
  updated_at: string
  references?: any[]
}

export interface UpdateChapterRequest {
  title?: string
  specialty?: string
  status?: string
  content?: any
  metadata?: any
}

// Reference types
export interface Reference {
  id: string
  title: string
  authors: string[]
  year?: number
  journal?: string
  doi?: string
  pmid?: string
  url?: string
  abstract?: string
  created_at: string
}

export interface CreateReferenceRequest {
  title: string
  authors: string[]
  year?: number
  journal?: string
  doi?: string
  pmid?: string
  url?: string
  abstract?: string
}

// Q&A types
export interface QAQuestion {
  id: string
  question: string
  answer: string
  context?: string
  chapter_id?: string
  confidence?: number
  sources?: any[]
  created_at: string
}

// Procedure types
export interface Procedure {
  id: string
  name: string
  category: string
  specialty: string
  description?: string
  steps?: any[]
  complications?: any[]
  contraindications?: any[]
  evidence_level?: string
  created_at: string
  updated_at: string
}

export interface SurgicalProcedure extends Procedure {
  complexity?: 'basic' | 'intermediate' | 'advanced'
  duration_minutes?: number
  anesthesia_type?: string
  equipment?: string[]
  success_rate?: number
}

// Search types
export interface SearchResult {
  id: string
  type: 'chapter' | 'reference' | 'procedure'
  title: string
  excerpt: string
  score: number
  metadata?: any
  url?: string
  relevance_score?: number
}

// Synthesis types
export interface SynthesisRequest {
  topic: string
  specialty: string
  max_sources?: number
  depth?: 'basic' | 'intermediate' | 'comprehensive'
}

export interface SynthesisResult {
  chapter_id: string
  title: string
  content: any
  success: boolean
  error?: string
}

export type CustomType = any
