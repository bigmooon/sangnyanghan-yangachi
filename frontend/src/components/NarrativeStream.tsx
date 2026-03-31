import { useSSE } from '../hooks/useSSE'

interface Props {
  url: string | null
  fallbackText?: string
}

export function NarrativeStream({ url, fallbackText }: Props) {
  const { text, isStreaming } = useSSE(url)
  const displayText = text || fallbackText || ''

  if (!displayText && !isStreaming) return null

  return (
    <div className="narrative-box pixel-box">
      <span className="pixel-label text-cyan">◆ NARRATIVE</span>
      <p className="narrative-text">
        {displayText}
        {isStreaming && <span className="cursor-blink">█</span>}
      </p>
    </div>
  )
}
