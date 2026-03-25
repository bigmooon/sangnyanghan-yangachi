import { useNavigate } from 'react-router-dom'
import { useState } from 'react'
import { useGameSession } from '../hooks/useGameSession'

const CHARACTERS = [
  {
    id: 1,
    name: '반휘혈',
    emoji: '😤',
    title: 'THE DELINQUENT',
    description: '냉혹한 카리스마.\n세상에서 가장 무서운 아우라.',
    initial: { yangachi: 70, kindness: 30 },
    color: '#ff6b35',
    difficulty: '어려움',
  },
  {
    id: 2,
    name: '나카무라',
    emoji: '😎',
    title: 'THE BALANCED',
    description: '일본 예의와 조직 문화의\n완벽한 조화.',
    initial: { yangachi: 50, kindness: 50 },
    color: '#ffd700',
    difficulty: '보통',
  },
  {
    id: 3,
    name: '임길순',
    emoji: '😇',
    title: 'THE KIND ONE',
    description: '순진해 보이지만\n선천적으로 착한 마음.',
    initial: { yangachi: 30, kindness: 70 },
    color: '#00ff41',
    difficulty: '쉬움',
  },
]

interface Props {
  onGameStart: (gameState: import('../types/game').GameState) => void
}

export function CharacterSelect({ onGameStart }: Props) {
  const navigate = useNavigate()
  const { startGame, isLoading, error } = useGameSession()
  const [selected, setSelected] = useState<number | null>(null)
  const [starting, setStarting] = useState(false)

  const handleStart = async () => {
    if (selected === null) return
    setStarting(true)
    const state = await startGame(selected)
    if (state) {
      onGameStart(state)
      navigate('/game')
    }
    setStarting(false)
  }

  return (
    <div className="screen char-select">
      <div className="scanlines" />

      <div className="char-select-content">
        <div className="page-header">
          <button className="back-btn" onClick={() => navigate('/')}>◀ BACK</button>
          <h2 className="pixel-title">CHARACTER SELECT</h2>
        </div>

        <div className="char-grid">
          {CHARACTERS.map(char => (
            <div
              key={char.id}
              className={`char-card pixel-box ${selected === char.id ? 'char-selected' : ''}`}
              style={{ '--char-color': char.color } as React.CSSProperties}
              onClick={() => setSelected(char.id)}
            >
              <div className="char-emoji">{char.emoji}</div>
              <div className="char-title" style={{ color: char.color }}>{char.title}</div>
              <div className="char-name">{char.name}</div>
              <div className="char-desc">{char.description.split('\n').map((l, i) => (
                <span key={i}>{l}<br /></span>
              ))}</div>
              <div className="char-stats-preview">
                <div className="mini-stat">
                  <span style={{ color: '#ff6b35' }}>양아치 </span>
                  <span>{'█'.repeat(Math.round(char.initial.yangachi / 10))}</span>
                </div>
                <div className="mini-stat">
                  <span style={{ color: '#00ff41' }}>친절함 </span>
                  <span>{'█'.repeat(Math.round(char.initial.kindness / 10))}</span>
                </div>
              </div>
              <div className="char-difficulty" style={{ color: char.color }}>
                ★ {char.difficulty}
              </div>
              {selected === char.id && (
                <div className="selected-badge blink">SELECTED</div>
              )}
            </div>
          ))}
        </div>

        {error && <p className="text-red pixel-box">{error}</p>}

        <div className="char-select-footer">
          <button
            className="pixel-btn btn-primary btn-large"
            onClick={handleStart}
            disabled={selected === null || isLoading || starting}
          >
            {isLoading || starting ? '[ LOADING... ]' : '▶ START GAME'}
          </button>
        </div>
      </div>
    </div>
  )
}
