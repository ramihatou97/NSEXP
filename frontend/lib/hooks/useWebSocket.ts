/**
 * WebSocket Hook for Real-time Synthesis Progress
 * Handles WebSocket connection and synthesis progress updates
 */

import { useState, useEffect, useCallback, useRef } from 'react'

const WS_URL = process.env.NEXT_PUBLIC_WS_URL || 'ws://localhost:8000'

interface SynthesisProgress {
  status: 'searching' | 'analyzing' | 'synthesizing' | 'generating' | 'completed' | 'failed'
  message: string
  progress: number
  step?: string
  details?: string
}

interface SynthesisResult {
  chapter_id: string
  title: string
  content?: any
  success?: boolean
}

interface UseSynthesisWithProgressReturn {
  startSynthesis: (topic: string, specialty: string, maxSources?: number) => Promise<void>
  reset: () => void
  isGenerating: boolean
  progress: SynthesisProgress | null
  result: SynthesisResult | null
  error: Error | null
  isConnected: boolean
}

/**
 * Hook for synthesis with WebSocket progress updates
 */
export function useSynthesisWithProgress(): UseSynthesisWithProgressReturn {
  const [isGenerating, setIsGenerating] = useState(false)
  const [progress, setProgress] = useState<SynthesisProgress | null>(null)
  const [result, setResult] = useState<SynthesisResult | null>(null)
  const [error, setError] = useState<Error | null>(null)
  const [isConnected, setIsConnected] = useState(false)
  
  const wsRef = useRef<WebSocket | null>(null)
  const reconnectTimeoutRef = useRef<NodeJS.Timeout>()
  const reconnectAttemptsRef = useRef(0)
  const maxReconnectAttempts = 5

  /**
   * Connect to WebSocket server
   */
  const connect = useCallback(() => {
    if (typeof window === 'undefined') return // Only run in browser

    try {
      const ws = new WebSocket(`${WS_URL}/ws`)
      wsRef.current = ws

      ws.onopen = () => {
        console.log('WebSocket connected')
        setIsConnected(true)
        reconnectAttemptsRef.current = 0
      }

      ws.onmessage = (event) => {
        try {
          const data = JSON.parse(event.data)
          
          // Handle different message types
          switch (data.type) {
            case 'synthesis_progress':
              setProgress({
                status: data.status,
                message: data.message,
                progress: data.progress,
                step: data.step,
                details: data.details,
              })
              break
              
            case 'synthesis_complete':
              setIsGenerating(false)
              setResult({
                chapter_id: data.chapter_id,
                title: data.title,
                content: data.content,
                success: true,
              })
              setProgress({
                status: 'completed',
                message: 'Synthesis completed successfully!',
                progress: 100,
              })
              break
              
            case 'synthesis_error':
              setIsGenerating(false)
              setError(new Error(data.error || 'Synthesis failed'))
              setProgress({
                status: 'failed',
                message: data.error || 'Synthesis failed',
                progress: 0,
              })
              break
              
            case 'pong':
              // Heartbeat response
              break
              
            default:
              console.log('Unknown WebSocket message type:', data.type)
          }
        } catch (err) {
          console.error('Error parsing WebSocket message:', err)
        }
      }

      ws.onerror = (event) => {
        console.error('WebSocket error:', event)
        setIsConnected(false)
      }

      ws.onclose = () => {
        console.log('WebSocket disconnected')
        setIsConnected(false)
        wsRef.current = null

        // Attempt to reconnect
        if (reconnectAttemptsRef.current < maxReconnectAttempts) {
          reconnectAttemptsRef.current++
          const delay = Math.min(1000 * Math.pow(2, reconnectAttemptsRef.current), 30000)
          console.log(`Reconnecting in ${delay}ms (attempt ${reconnectAttemptsRef.current})`)
          
          reconnectTimeoutRef.current = setTimeout(() => {
            connect()
          }, delay)
        }
      }
    } catch (err) {
      console.error('Error creating WebSocket:', err)
      setIsConnected(false)
    }
  }, [])

  /**
   * Disconnect from WebSocket server
   */
  const disconnect = useCallback(() => {
    if (reconnectTimeoutRef.current) {
      clearTimeout(reconnectTimeoutRef.current)
    }
    
    if (wsRef.current) {
      wsRef.current.close()
      wsRef.current = null
    }
  }, [])

  /**
   * Send message via WebSocket
   */
  const sendMessage = useCallback((message: any) => {
    if (wsRef.current?.readyState === WebSocket.OPEN) {
      wsRef.current.send(JSON.stringify(message))
      return true
    }
    return false
  }, [])

  /**
   * Start synthesis process
   */
  const startSynthesis = useCallback(async (
    topic: string,
    specialty: string,
    maxSources: number = 15
  ) => {
    try {
      setIsGenerating(true)
      setProgress({
        status: 'searching',
        message: 'Initializing synthesis...',
        progress: 0,
      })
      setResult(null)
      setError(null)

      // If WebSocket is connected, request via WebSocket for real-time updates
      if (isConnected) {
        const sent = sendMessage({
          type: 'synthesis_request',
          topic,
          specialty,
          max_sources: maxSources,
        })

        if (sent) {
          return // WebSocket will handle the rest
        }
      }

      // Fallback to HTTP API if WebSocket is not available
      const API_BASE_URL = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000/api/v1'
      const response = await fetch(`${API_BASE_URL}/synthesis/generate`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({
          topic,
          specialty,
          max_sources: maxSources,
        }),
      })

      if (!response.ok) {
        throw new Error(`Synthesis failed: ${response.statusText}`)
      }

      const data = await response.json()

      if (data.success) {
        setResult({
          chapter_id: data.chapter_id,
          title: data.chapter?.title || topic,
          content: data.chapter,
          success: true,
        })
        setProgress({
          status: 'completed',
          message: 'Synthesis completed!',
          progress: 100,
        })
      } else {
        throw new Error(data.error || 'Synthesis failed')
      }
    } catch (err) {
      console.error('Synthesis error:', err)
      setError(err instanceof Error ? err : new Error('Synthesis failed'))
      setProgress({
        status: 'failed',
        message: err instanceof Error ? err.message : 'Synthesis failed',
        progress: 0,
      })
    } finally {
      setIsGenerating(false)
    }
  }, [isConnected, sendMessage])

  /**
   * Reset state
   */
  const reset = useCallback(() => {
    setIsGenerating(false)
    setProgress(null)
    setResult(null)
    setError(null)
  }, [])

  // Connect on mount, disconnect on unmount
  useEffect(() => {
    connect()
    return () => {
      disconnect()
    }
  }, [connect, disconnect])

  // Heartbeat to keep connection alive
  useEffect(() => {
    if (!isConnected) return

    const interval = setInterval(() => {
      sendMessage({ type: 'ping' })
    }, 30000) // Every 30 seconds

    return () => clearInterval(interval)
  }, [isConnected, sendMessage])

  return {
    startSynthesis,
    reset,
    isGenerating,
    progress,
    result,
    error,
    isConnected,
  }
}
