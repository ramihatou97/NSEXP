/**
 * API Client for NSEXP Backend
 * Basic API service for backend communication
 */

const API_BASE_URL = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000/api/v1'

/**
 * Base fetch wrapper with error handling
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
    throw new Error(`API Error: ${response.statusText}`)
  }

  return response.json()
}

/**
 * API service object
 */
export const api = {
  chapters: {
    list: () => fetchAPI('/chapters'),
    get: (id: string) => fetchAPI(`/chapters/${id}`),
    create: (data: any) => fetchAPI('/chapters', {
      method: 'POST',
      body: JSON.stringify(data),
    }),
    update: (id: string, data: any) => fetchAPI(`/chapters/${id}`, {
      method: 'PUT',
      body: JSON.stringify(data),
    }),
    delete: (id: string) => fetchAPI(`/chapters/${id}`, {
      method: 'DELETE',
    }),
  },
  qa: {
    ask: (data: any) => fetchAPI('/qa/ask', {
      method: 'POST',
      body: JSON.stringify(data),
    }),
  },
  synthesis: {
    generate: (data: any) => fetchAPI('/synthesis/generate', {
      method: 'POST',
      body: JSON.stringify(data),
    }),
  },
}
