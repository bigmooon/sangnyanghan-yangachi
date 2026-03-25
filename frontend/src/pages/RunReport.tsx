import { useNavigate, useLocation } from 'react-router-dom'
import { useEffect, useState } from 'react'
import type { GameState } from '../types/game'

interface LocationState {
  gameState: GameState | null
  endingMessage: string | null
}

const ENDING_DATA: Record<string, { title: string; stars: number; color: string; desc: string }> = {
  full_yangachi: {
    title: '완전한 양아치',
    stars: 1,
    color: '#ff6b35',
    desc: '모든 것을 잃고 진정한 악당이 되었다.',
  },
  feared_but_respected: {
    title: '공포의 대상',
    stars: 3,
    color: '#ff6b35',
    desc: '두려움 속에서도 존중받는 존재.',
  },
  true_kind_delinquent: {
    title: '진정한 상냥한 양아치',
    stars: 5,
    color: '#00ff41',
    desc: '양아치이면서도 진심으로 상냥한 사람.',
  },
  saint: {
    title: '성인군자',
    stars: 4,
    color: '#00d4ff',
    desc: '순수한 선함으로 모든 이를 감동시켰다.',
  },
  outcast: {
    title: '왕따',
    stars: 1,
    color: '#888888',
    desc: '사회로부터 완전히 배척당했다.',
  },
  balanced: {
    title: '균형잡힌 삶',
    stars: 3,
    color: '#ffd700',
    desc: '양아치와 친절함 사이에서 균형을 찾았다.',
  },
  survived: {
    title: '생존자',
    stars: 2,
    color: '#e0e0e0',
    desc: '어떻게든 살아남았다.',
  },
}

export function RunReport() {
  const navigate = useNavigate()
  const location = useLocation()
  const { gameState, endingMessage } = (location.state as LocationState) ?? {}

  const [visible, setVisible] = useState(false)

  useEffect(() => {
    if (!gameState) {
      navigate('/')
      return
    }
    const t = setTimeout(() => setVisible(true), 200)
    return () => clearTimeout(t)
  }, [gameState, navigate])

  if (!gameState) return null

  const endingType = gameState.ending_type ?? 'survived'
  const ending = ENDING_DATA[endingType] ?? ENDING_DATA.survived

  return (
    <div className="screen run-report">
      <div className="scanlines" />

      <div className={`report-content ${visible ? 'fade-in' : 'hidden'}`}>
        <div className="report-header">
          <h1 className="pixel-title">RUN REPORT</h1>
          <div className="report-divider" />
        </div>

        {/* Ending result */}
        <div className="ending-card pixel-box" style={{ borderColor: ending.color }}>
          <div className="ending-stars-big" style={{ color: ending.color }}>
            {'★'.repeat(ending.stars)}{'☆'.repeat(5 - ending.stars)}
          </div>
          <h2 className="ending-title" style={{ color: ending.color }}>
            {ending.title}
          </h2>
          <p className="ending-desc">{ending.desc}</p>
        </div>

        {/* Final stats */}
        <div className="final-stats pixel-box">
          <span className="pixel-label">FINAL STATS</span>
          <div className="final-stat-grid">
            <div className="final-stat">
              <span className="text-orange">양아치</span>
              <span className="final-stat-val">{gameState.stats.yangachi}</span>
            </div>
            <div className="final-stat">
              <span className="text-green">친절함</span>
              <span className="final-stat-val">{gameState.stats.kindness}</span>
            </div>
            <div className="final-stat">
              <span className="text-cyan">평판</span>
              <span className="final-stat-val">
                {gameState.stats.reputation > 0
                  ? `+${gameState.stats.reputation}`
                  : gameState.stats.reputation}
              </span>
            </div>
            <div className="final-stat">
              <span className="text-yellow">턴</span>
              <span className="final-stat-val">
                {gameState.turn}/{gameState.max_turns}
              </span>
            </div>
          </div>
        </div>

        {/* Ending message */}
        {(endingMessage ?? gameState.game_over_reason) && (
          <div className="ending-message pixel-box">
            <p>{endingMessage ?? gameState.game_over_reason}</p>
          </div>
        )}

        {/* Actions */}
        <div className="report-actions">
          <button
            className="pixel-btn btn-primary btn-large"
            onClick={() => navigate('/character-select')}
          >
            ▶ PLAY AGAIN
          </button>
          <button
            className="pixel-btn btn-secondary"
            onClick={() => navigate('/')}
          >
            MAIN MENU
          </button>
        </div>
      </div>
    </div>
  )
}
