/**
 * Import API Module
 * Handles importing chapters from files
 */

const API_BASE_URL = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000/api/v1'

export interface ImportResponse {
  success: boolean
  message?: string
  chapter_id?: string
  data?: any
  error?: string
}

/**
 * Import chapter from file
 */
async function importChapterFromFile(file: File): Promise<ImportResponse> {
  try {
    // Read file content
    const content = await readFileContent(file)
    const fileExtension = file.name.split('.').pop()?.toLowerCase()

    // Parse content based on file type
    let data: any

    if (fileExtension === 'json') {
      data = JSON.parse(content)
    } else if (fileExtension === 'md' || fileExtension === 'markdown') {
      data = parseMarkdown(content)
    } else {
      throw new Error(`Unsupported file format: ${fileExtension}`)
    }

    // Send import request
    const response = await fetch(`${API_BASE_URL}/import`, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
      },
      body: JSON.stringify(data),
    })

    if (!response.ok) {
      throw new Error(`Import failed: ${response.statusText}`)
    }

    return await response.json()
  } catch (error) {
    console.error('Import error:', error)
    return {
      success: false,
      error: error instanceof Error ? error.message : 'Import failed',
    }
  }
}

/**
 * Read file content as text
 */
function readFileContent(file: File): Promise<string> {
  return new Promise((resolve, reject) => {
    const reader = new FileReader()
    reader.onload = (e) => resolve(e.target?.result as string)
    reader.onerror = (e) => reject(new Error('Failed to read file'))
    reader.readAsText(file)
  })
}

/**
 * Parse Markdown file into chapter data
 * Simple parser that extracts title and content
 */
function parseMarkdown(markdown: string): any {
  const lines = markdown.split('\n')
  let title = 'Untitled Chapter'
  let specialty = 'Neurosurgery General'
  let content: any = {}
  let currentSection = ''
  const sections: { [key: string]: string } = {}

  for (let i = 0; i < lines.length; i++) {
    const line = lines[i]

    // Extract title (first # heading)
    if (line.startsWith('# ') && title === 'Untitled Chapter') {
      title = line.substring(2).trim()
      continue
    }

    // Extract specialty from metadata
    if (line.startsWith('**Specialty:**')) {
      specialty = line.split('**Specialty:**')[1].trim()
      continue
    }

    // Section headings (## or ###)
    if (line.startsWith('## ') || line.startsWith('### ')) {
      currentSection = line.replace(/^#+\s+/, '').trim()
      sections[currentSection] = ''
      continue
    }

    // Accumulate content in current section
    if (currentSection && line.trim()) {
      sections[currentSection] += line + '\n'
    }
  }

  // Build content object from sections
  content = {
    sections: Object.entries(sections).map(([title, text]) => ({
      title,
      content: text.trim(),
    })),
    raw_markdown: markdown,
  }

  return {
    title,
    specialty,
    content,
    status: 'draft',
    metadata: {
      imported_from: 'markdown',
      imported_at: new Date().toISOString(),
    },
  }
}

/**
 * Import API object
 */
export const importApi = {
  importChapterFromFile,
}
