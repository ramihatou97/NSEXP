/**
 * API client for enhanced backend services
 * Supports all new v2.2.0 endpoints
 */

const API_BASE_URL = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000/api/v1';

/**
 * Image Extraction & Analysis
 */
export interface ImageExtractionRequest {
  pdf_path: string;
  output_dir?: string;
  min_width?: number;
  min_height?: number;
  extract_text?: boolean;
}

export interface ExtractedImage {
  page_number: number;
  image_index: number;
  filename: string;
  path?: string;
  width: number;
  height: number;
  format: string;
  type: string;
  extracted_text?: string;
  size_bytes: number;
}

export interface ImageExtractionResponse {
  success: boolean;
  pdf_path: string;
  total_pages: number;
  images_extracted: number;
  images: ExtractedImage[];
  output_directory?: string;
}

export async function extractImagesFromPDF(
  request: ImageExtractionRequest
): Promise<ImageExtractionResponse> {
  const response = await fetch(`${API_BASE_URL}/images/extract`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify(request),
  });
  
  if (!response.ok) {
    throw new Error(`Image extraction failed: ${response.statusText}`);
  }
  
  return response.json();
}

export async function analyzeAnatomicalImage(
  imagePath: string
): Promise<any> {
  const response = await fetch(`${API_BASE_URL}/images/analyze`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ image_path: imagePath }),
  });
  
  if (!response.ok) {
    throw new Error(`Image analysis failed: ${response.statusText}`);
  }
  
  return response.json();
}

/**
 * Comprehensive Synthesis
 */
export interface ComprehensiveSynthesisRequest {
  topic: string;
  specialty: string;
  references?: any[];
  focus_areas?: string[];
  include_images?: boolean;
}

export interface QualityMetrics {
  completeness_score: number;
  total_words: number;
  average_section_length: number;
  reference_density: number;
  has_images: boolean;
  image_count: number;
  estimated_reading_time_minutes: number;
}

export interface ComprehensiveSynthesisResponse {
  success: boolean;
  topic: string;
  specialty: string;
  sections: Record<string, string>;
  section_count: number;
  total_words: number;
  references: string[];
  reference_count: number;
  images: any[];
  image_count: number;
  quality_metrics: QualityMetrics;
  generated_at: string;
}

export async function synthesizeComprehensiveChapter(
  request: ComprehensiveSynthesisRequest
): Promise<ComprehensiveSynthesisResponse> {
  const response = await fetch(`${API_BASE_URL}/synthesis/comprehensive`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify(request),
  });
  
  if (!response.ok) {
    throw new Error(`Comprehensive synthesis failed: ${response.statusText}`);
  }
  
  return response.json();
}

export interface SummaryRequest {
  chapter_content: any;
  summary_type?: 'executive' | 'detailed' | 'technical' | 'bullet_points';
}

export async function generateChapterSummary(
  request: SummaryRequest
): Promise<any> {
  const response = await fetch(`${API_BASE_URL}/synthesis/summary`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify(request),
  });
  
  if (!response.ok) {
    throw new Error(`Summary generation failed: ${response.statusText}`);
  }
  
  return response.json();
}

/**
 * Deep Literature Search
 */
export interface DeepSearchRequest {
  query: string;
  sources?: string[];
  max_results?: number;
  filters?: {
    year_min?: number;
    year_max?: number;
  };
}

export interface SearchResult {
  source: string;
  pmid?: string;
  arxiv_id?: string;
  title: string;
  abstract: string;
  authors: string[];
  journal?: string;
  year: string;
  doi?: string;
  url: string;
  relevance_score: number;
}

export interface DeepSearchResponse {
  query: string;
  sources_searched: string[];
  total_results: number;
  results: SearchResult[];
  search_metadata: any;
}

export async function deepLiteratureSearch(
  request: DeepSearchRequest
): Promise<DeepSearchResponse> {
  const response = await fetch(`${API_BASE_URL}/search/deep`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify(request),
  });
  
  if (!response.ok) {
    throw new Error(`Deep search failed: ${response.statusText}`);
  }
  
  return response.json();
}

export async function enrichReference(reference: any): Promise<any> {
  const response = await fetch(`${API_BASE_URL}/references/enrich`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify(reference),
  });
  
  if (!response.ok) {
    throw new Error(`Reference enrichment failed: ${response.statusText}`);
  }
  
  return response.json();
}

/**
 * Advanced PDF Processing
 */
export interface AdvancedPDFRequest {
  pdf_path: string;
  extract_images?: boolean;
  extract_tables?: boolean;
}

export async function processAdvancedPDF(
  request: AdvancedPDFRequest
): Promise<any> {
  const response = await fetch(`${API_BASE_URL}/pdf/process-advanced`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify(request),
  });
  
  if (!response.ok) {
    throw new Error(`PDF processing failed: ${response.statusText}`);
  }
  
  return response.json();
}

export interface ChunkPDFRequest {
  pdf_path: string;
  chunk_size?: number;
  overlap?: number;
}

export async function chunkPDFContent(
  request: ChunkPDFRequest
): Promise<any> {
  const response = await fetch(`${API_BASE_URL}/pdf/chunk`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify(request),
  });
  
  if (!response.ok) {
    throw new Error(`PDF chunking failed: ${response.statusText}`);
  }
  
  return response.json();
}

/**
 * Alive Chapter Features
 */
export async function getAliveChapterStatus(): Promise<any> {
  const response = await fetch(`${API_BASE_URL}/alive-chapters/status`);
  
  if (!response.ok) {
    throw new Error(`Status check failed: ${response.statusText}`);
  }
  
  return response.json();
}

export async function activateChapter(
  chapterId: string,
  chapter: any
): Promise<any> {
  const response = await fetch(`${API_BASE_URL}/alive-chapters/activate`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ chapter_id: chapterId, chapter }),
  });
  
  if (!response.ok) {
    throw new Error(`Chapter activation failed: ${response.statusText}`);
  }
  
  return response.json();
}

export async function askChapterQuestion(
  chapterId: string,
  question: string,
  userId?: string,
  context?: string
): Promise<any> {
  const response = await fetch(`${API_BASE_URL}/alive-chapters/qa`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({
      chapter_id: chapterId,
      question,
      user_id: userId,
      context,
    }),
  });
  
  if (!response.ok) {
    throw new Error(`Question failed: ${response.statusText}`);
  }
  
  return response.json();
}

export async function getChapterCitations(chapterId: string): Promise<any> {
  const response = await fetch(
    `${API_BASE_URL}/alive-chapters/citations/${chapterId}`
  );
  
  if (!response.ok) {
    throw new Error(`Citation retrieval failed: ${response.statusText}`);
  }
  
  return response.json();
}

export async function suggestChapterCitations(
  chapterId: string,
  content: string
): Promise<any> {
  const response = await fetch(
    `${API_BASE_URL}/alive-chapters/citations/suggest`,
    {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ chapter_id: chapterId, content }),
    }
  );
  
  if (!response.ok) {
    throw new Error(`Citation suggestion failed: ${response.statusText}`);
  }
  
  return response.json();
}

export async function mergeChapterKnowledge(
  chapterId: string,
  newContent: string,
  source: string,
  metadata?: any
): Promise<any> {
  const response = await fetch(`${API_BASE_URL}/alive-chapters/merge`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({
      chapter_id: chapterId,
      new_content: newContent,
      source,
      metadata,
    }),
  });
  
  if (!response.ok) {
    throw new Error(`Knowledge merge failed: ${response.statusText}`);
  }
  
  return response.json();
}

export async function getChapterHealth(
  chapterId: string,
  userId?: string
): Promise<any> {
  const params = new URLSearchParams();
  if (userId) params.append('user_id', userId);
  
  const response = await fetch(
    `${API_BASE_URL}/alive-chapters/health/${chapterId}?${params}`
  );
  
  if (!response.ok) {
    throw new Error(`Health check failed: ${response.statusText}`);
  }
  
  return response.json();
}

export async function evolveChapter(
  chapterId: string,
  userId?: string
): Promise<any> {
  const response = await fetch(
    `${API_BASE_URL}/alive-chapters/evolve/${chapterId}`,
    {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ user_id: userId }),
    }
  );
  
  if (!response.ok) {
    throw new Error(`Chapter evolution failed: ${response.statusText}`);
  }
  
  return response.json();
}

export async function getBehavioralSuggestions(
  userId?: string,
  chapterId?: string
): Promise<any> {
  const params = new URLSearchParams();
  if (userId) params.append('user_id', userId);
  if (chapterId) params.append('chapter_id', chapterId);
  
  const response = await fetch(
    `${API_BASE_URL}/alive-chapters/suggestions?${params}`
  );
  
  if (!response.ok) {
    throw new Error(`Suggestion retrieval failed: ${response.statusText}`);
  }
  
  return response.json();
}
