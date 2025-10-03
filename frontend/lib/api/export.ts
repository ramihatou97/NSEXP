/**
 * Export API Module
 * Handles exporting chapters in various formats
 */

const API_BASE_URL = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000/api/v1'

export type ExportFormat = 'json' | 'markdown' | 'md' | 'html' | 'pdf' | 'docx'

export interface ExportResponse {
  success: boolean
  format?: string
  content?: string
  filename?: string
  mime_type?: string
  error?: string
}

/**
 * Export chapter in specified format
 */
async function exportChapter(chapterId: string, format: ExportFormat): Promise<ExportResponse> {
  try {
    const response = await fetch(
      `${API_BASE_URL}/export/${chapterId}?format=${format}`,
      {
        method: 'GET',
        headers: {
          'Content-Type': 'application/json',
        },
      }
    )

    if (!response.ok) {
      throw new Error(`Export failed: ${response.statusText}`)
    }

    return await response.json()
  } catch (error) {
    console.error('Export error:', error)
    return {
      success: false,
      error: error instanceof Error ? error.message : 'Export failed',
    }
  }
}

/**
 * Download chapter as file
 */
async function downloadChapter(chapterId: string, format: ExportFormat): Promise<void> {
  const result = await exportChapter(chapterId, format)

  if (!result.success || !result.content) {
    throw new Error(result.error || 'Export failed')
  }

  // Create blob and download
  const blob = new Blob([result.content], { type: result.mime_type || 'text/plain' })
  const url = window.URL.createObjectURL(blob)
  const a = document.createElement('a')
  a.href = url
  a.download = result.filename || `chapter.${format}`
  document.body.appendChild(a)
  a.click()
  window.URL.revokeObjectURL(url)
  document.body.removeChild(a)
}

/**
 * Export API object
 */
export const exportApi = {
  exportChapter,
  downloadChapter,
}
