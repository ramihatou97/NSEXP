/**
 * Tests for API service
 * Tests backend API integration
 */

import { api } from '@/services/api'

// Mock fetch globally
global.fetch = jest.fn()

describe('API Service', () => {
  beforeEach(() => {
    // Clear all mocks before each test
    jest.clearAllMocks()
  })

  describe('Chapter API', () => {
    it('should fetch chapters list', async () => {
      const mockChapters = [
        { id: '1', title: 'Test Chapter 1', specialty: 'tumor' },
        { id: '2', title: 'Test Chapter 2', specialty: 'vascular' },
      ]

      ;(global.fetch as jest.Mock).mockResolvedValueOnce({
        ok: true,
        json: async () => mockChapters,
      })

      const result = await api.chapters.list()
      expect(result).toEqual(mockChapters)
      expect(global.fetch).toHaveBeenCalledTimes(1)
    })

    it('should fetch single chapter', async () => {
      const mockChapter = {
        id: '1',
        title: 'Glioblastoma Management',
        specialty: 'tumor',
        content: 'Test content',
      }

      ;(global.fetch as jest.Mock).mockResolvedValueOnce({
        ok: true,
        json: async () => mockChapter,
      })

      const result = await api.chapters.get('1')
      expect(result).toEqual(mockChapter)
    })

    it('should create new chapter', async () => {
      const newChapter = {
        title: 'New Chapter',
        specialty: 'spine',
        content: 'New content',
      }

      const mockResponse = { ...newChapter, id: '3' }

      ;(global.fetch as jest.Mock).mockResolvedValueOnce({
        ok: true,
        json: async () => mockResponse,
      })

      const result = await api.chapters.create(newChapter)
      expect(result).toEqual(mockResponse)
    })

    it('should handle API errors', async () => {
      ;(global.fetch as jest.Mock).mockResolvedValueOnce({
        ok: false,
        status: 404,
        statusText: 'Not Found',
      })

      await expect(api.chapters.get('999')).rejects.toThrow()
    })
  })

  describe('Q&A API', () => {
    it('should submit question', async () => {
      const question = {
        question: 'What are the indications for surgery?',
        specialty: 'general',
      }

      const mockResponse = {
        answer: 'Indications include...',
        references: [],
      }

      ;(global.fetch as jest.Mock).mockResolvedValueOnce({
        ok: true,
        json: async () => mockResponse,
      })

      const result = await api.qa.ask(question)
      expect(result).toEqual(mockResponse)
    })
  })

  describe('Synthesis API', () => {
    it('should generate synthesis', async () => {
      const synthesisRequest = {
        chapter_id: '1',
        sections: ['introduction', 'methods'],
      }

      const mockResponse = {
        content: 'Generated synthesis...',
        status: 'completed',
      }

      ;(global.fetch as jest.Mock).mockResolvedValueOnce({
        ok: true,
        json: async () => mockResponse,
      })

      const result = await api.synthesis.generate(synthesisRequest)
      expect(result).toEqual(mockResponse)
    })
  })
})
