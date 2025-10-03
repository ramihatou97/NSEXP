/**
 * Custom React Hooks
 * Collection of reusable hooks for the application
 */

import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query'

const API_BASE_URL = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000/api/v1'

/**
 * Fetch helper with error handling
 */
async function fetchAPI(endpoint: string, options?: RequestInit) {
  const url = `${API_BASE_URL}${endpoint}`
  const response = await fetch(url, {
    ...options,
    headers: {
      'Content-Type': 'application/json',
      ...options?.headers,
    },
  })

  if (!response.ok) {
    const error = await response.json().catch(() => ({ message: response.statusText }))
    throw new Error(error.message || `API Error: ${response.statusText}`)
  }

  return response.json()
}

/**
 * Hook to fetch a single chapter
 */
export function useChapter(chapterId: string) {
  return useQuery({
    queryKey: ['chapter', chapterId],
    queryFn: () => fetchAPI(`/chapters/${chapterId}`),
    enabled: !!chapterId,
  })
}

/**
 * Hook to fetch all chapters
 */
export function useChapters(options?: { 
  limit?: number
  specialty?: string
  status?: string
}) {
  const queryParams = new URLSearchParams()
  if (options?.limit) queryParams.append('limit', String(options.limit))
  if (options?.specialty) queryParams.append('specialty', options.specialty)
  if (options?.status) queryParams.append('status', options.status)
  
  const queryString = queryParams.toString()
  return useQuery({
    queryKey: ['chapters', options],
    queryFn: () => fetchAPI(`/chapters${queryString ? `?${queryString}` : ''}`),
  })
}

/**
 * Hook to delete a chapter
 */
export function useDeleteChapter() {
  const queryClient = useQueryClient()

  return useMutation({
    mutationFn: (chapterId: string) => 
      fetchAPI(`/chapters/${chapterId}`, {
        method: 'DELETE',
      }),
    onSuccess: () => {
      // Invalidate chapters list to refetch
      queryClient.invalidateQueries({ queryKey: ['chapters'] })
    },
  })
}

/**
 * Hook to create a chapter
 */
export function useCreateChapter() {
  const queryClient = useQueryClient()

  return useMutation({
    mutationFn: (data: any) =>
      fetchAPI('/chapters', {
        method: 'POST',
        body: JSON.stringify(data),
      }),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['chapters'] })
    },
  })
}

/**
 * Hook to update a chapter
 */
export function useUpdateChapter(chapterId?: string) {
  const queryClient = useQueryClient()

  return useMutation({
    mutationFn: ({ id, data }: { id?: string; data: any }) => {
      const targetId = id || chapterId
      if (!targetId) throw new Error('Chapter ID is required')
      return fetchAPI(`/chapters/${targetId}`, {
        method: 'PUT',
        body: JSON.stringify(data),
      })
    },
    onSuccess: (_, variables) => {
      const targetId = variables.id || chapterId
      if (targetId) {
        queryClient.invalidateQueries({ queryKey: ['chapter', targetId] })
      }
      queryClient.invalidateQueries({ queryKey: ['chapters'] })
    },
  })
}

/**
 * Hook for citation network
 */
export function useCitationNetwork(chapterId?: string | null) {
  const queryParam = chapterId ? `?chapter_id=${chapterId}` : ''
  return useQuery({
    queryKey: ['citation-network', chapterId],
    queryFn: () => fetchAPI(`/citations/network${queryParam}`),
    enabled: true,
  })
}

/**
 * Hook to fetch all procedures
 */
export function useProcedures(options?: {
  procedure_type?: string
  anatomical_region?: string
}) {
  const queryParams = new URLSearchParams()
  if (options?.procedure_type) queryParams.append('procedure_type', options.procedure_type)
  if (options?.anatomical_region) queryParams.append('anatomical_region', options.anatomical_region)
  
  const queryString = queryParams.toString()
  return useQuery({
    queryKey: ['procedures', options],
    queryFn: () => fetchAPI(`/procedures${queryString ? `?${queryString}` : ''}`),
  })
}

/**
 * Hook to fetch a single procedure
 */
export function useProcedure(procedureId: string | null) {
  return useQuery({
    queryKey: ['procedure', procedureId],
    queryFn: () => fetchAPI(`/procedures/${procedureId}`),
    enabled: !!procedureId,
  })
}

/**
 * Hook to ask a Q&A question
 */
export function useQAQuestion() {
  return useMutation({
    mutationFn: (data: { question: string; context?: string; chapter_id?: string }) =>
      fetchAPI('/qa/ask', {
        method: 'POST',
        body: JSON.stringify(data),
      }),
  })
}

/**
 * Hook to fetch Q&A history
 */
export function useQAHistory(options?: {
  chapter_id?: string
  limit?: number
}) {
  const queryParams = new URLSearchParams()
  if (options?.chapter_id) queryParams.append('chapter_id', options.chapter_id)
  if (options?.limit) queryParams.append('limit', String(options.limit))
  
  const queryString = queryParams.toString()
  return useQuery({
    queryKey: ['qa-history', options],
    queryFn: () => fetchAPI(`/qa/history${queryString ? `?${queryString}` : ''}`),
  })
}

/**
 * Hook to fetch all references
 */
export function useReferences(options?: { limit?: number }) {
  const queryParams = options?.limit ? `?limit=${options.limit}` : ''
  return useQuery({
    queryKey: ['references', options],
    queryFn: () => fetchAPI(`/references${queryParams}`),
  })
}

/**
 * Hook to create a reference
 */
export function useCreateReference() {
  const queryClient = useQueryClient()

  return useMutation({
    mutationFn: (data: any) =>
      fetchAPI('/references', {
        method: 'POST',
        body: JSON.stringify(data),
      }),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['references'] })
    },
  })
}

/**
 * Hook to delete a reference
 */
export function useDeleteReference() {
  const queryClient = useQueryClient()

  return useMutation({
    mutationFn: (referenceId: string) =>
      fetchAPI(`/references/${referenceId}`, {
        method: 'DELETE',
      }),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['references'] })
    },
  })
}

/**
 * Hook for basic search
 */
export function useSearch(params: { query: string; search_type?: string; limit?: number }, options?: any) {
  const queryParams = new URLSearchParams()
  if (params.query) queryParams.append('query', params.query)
  if (params.search_type) queryParams.append('search_type', params.search_type)
  if (params.limit) queryParams.append('limit', String(params.limit))
  
  const queryString = queryParams.toString()
  return useQuery({
    queryKey: ['search', params],
    queryFn: () => fetchAPI(`/search?${queryString}`),
    enabled: options?.enabled !== false && params.query.length > 0,
  })
}

/**
 * Hook for semantic search
 */
export function useSemanticSearch(params: { query: string; limit?: number }, options?: any) {
  return useQuery({
    queryKey: ['semantic-search', params],
    queryFn: () => fetchAPI('/search/semantic', {
      method: 'POST',
      body: JSON.stringify(params),
    }),
    enabled: options?.enabled !== false && params.query.length > 0,
  })
}

/**
 * Hook to fetch user preferences
 */
export function usePreferences() {
  return useQuery({
    queryKey: ['preferences'],
    queryFn: () => fetchAPI('/preferences'),
  })
}

/**
 * Hook to update user preferences
 */
export function useUpdatePreferences() {
  const queryClient = useQueryClient()

  return useMutation({
    mutationFn: (data: any) =>
      fetchAPI('/preferences', {
        method: 'PUT',
        body: JSON.stringify(data),
      }),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['preferences'] })
    },
  })
}

// Re-export WebSocket hooks
export * from './useWebSocket'
