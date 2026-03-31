import { useState, useEffect } from 'react'

export function useSSE(url: string | null) {
  const [text, setText] = useState('')
  const [isStreaming, setIsStreaming] = useState(false)

  useEffect(() => {
    if (!url) return

    setText('')
    setIsStreaming(true)

    const es = new EventSource(url)

    es.onmessage = (event) => {
      setText(prev => prev + event.data)
    }

    es.addEventListener('done', () => {
      setIsStreaming(false)
      es.close()
    })

    es.onerror = () => {
      setIsStreaming(false)
      es.close()
    }

    return () => {
      es.close()
    }
  }, [url])

  return { text, isStreaming }
}
