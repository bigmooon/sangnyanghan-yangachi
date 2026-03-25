import { useEffect, useState } from 'react'

interface Props {
  reason: string | null
  endingType: string | null
  onContinue: () => void
}

const ENDING_LABELS: Record<string, { label: string; stars: number; color: string }> = {
  full_yangachi: { label: '완전한 양아치', stars: 1, color: '#ff6b35' },
  feared_but_respected: { label: '공포의 대상', stars: 3, color: '#ff6b35' },
  true_kind_delinquent: { label: '진정한 상냥한 양아치', stars: 5, color: '#00ff41' },
  saint: { label: '성인군자', stars: 4, color: '#00d4ff' },
  outcast: { label: '왕따', stars: 1, color: '#888888' },
  balanced: { label: '균형잡힌 삶', stars: 3, color: '#ffd700' },
  survived: { label: '생존자', stars: 2, color: '#e0e0e0' },
}

export function GameOverModal({ reason, endingType, onContinue }: Props) {
  const [visible, setVisible] = useState(false)

  useEffect(() => {
    const t = setTimeout(() => setVisible(true), 100)
    return () => clearTimeout(t)
  }, [])

  const ending = endingType ? ENDING_LABELS[endingType] : null

  return (
    <div className={`modal-overlay ${visible ? 'modal-visible' : ''}`}>
      <div className="modal-box pixel-box">
        <div className="modal-header blink">
          ★ GAME OVER ★
        </div>

        {ending && (
          <div className="ending-result" style={{ color: ending.color }}>
            <div className="ending-label">{ending.label}</div>
            <div className="ending-stars">
              {'★'.repeat(ending.stars)}{'☆'.repeat(5 - ending.stars)}
            </div>
          </div>
        )}

        {reason && (
          <div className="game-over-reason">
            <p>{reason}</p>
          </div>
        )}

        <button className="pixel-btn btn-primary" onClick={onContinue}>
          [ 결과 보기 ]
        </button>
      </div>
    </div>
  )
}
