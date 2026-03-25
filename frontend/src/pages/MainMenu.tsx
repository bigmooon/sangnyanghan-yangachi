import { useNavigate } from 'react-router-dom'
import { useEffect, useState } from 'react'

const ASCII_LOGO = `
 ╔═══════════════════════════╗
 ║  상냥한 양아치로 살아남기   ║
 ╚═══════════════════════════╝`

export function MainMenu() {
  const navigate = useNavigate()
  const [showCursor, setShowCursor] = useState(true)
  const [titleVisible, setTitleVisible] = useState(false)

  useEffect(() => {
    const t = setTimeout(() => setTitleVisible(true), 300)
    const cursor = setInterval(() => setShowCursor(v => !v), 500)
    return () => {
      clearTimeout(t)
      clearInterval(cursor)
    }
  }, [])

  return (
    <div className="screen main-menu">
      <div className="scanlines" />

      <div className={`menu-content ${titleVisible ? 'fade-in' : 'hidden'}`}>
        <div className="game-logo">
          <pre className="ascii-logo">{ASCII_LOGO}</pre>
        </div>

        <div className="pixel-divider" />

        <div className="menu-subtitle">
          <span className="text-cyan">▶ LLM-POWERED TEXT ADVENTURE ◀</span>
        </div>

        <div className="menu-char-preview">
          <span className="char-sprite">🥷</span>
          <span className="char-sprite-shadow">🥷</span>
        </div>

        <div className="menu-buttons">
          <button
            className="pixel-btn btn-primary btn-large"
            onClick={() => navigate('/character-select')}
          >
            ▶ PLAY GAME
          </button>
        </div>

        <div className="menu-footer">
          <p className="text-gray">Press START to begin your journey</p>
          <p className="text-gray blink">{showCursor ? '█' : ' '}</p>
        </div>

        <div className="menu-info pixel-box">
          <p className="text-yellow">► 목표</p>
          <p>양아치이면서도 상냥한 사람으로</p>
          <p>10턴을 살아남아라</p>
          <br />
          <p className="text-cyan">► 스탯 경고</p>
          <p>양아치 100 → BAD END</p>
          <p>친절함 0 → BAD END</p>
        </div>
      </div>
    </div>
  )
}
