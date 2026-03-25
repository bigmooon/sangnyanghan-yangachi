import type { Stats } from '../types/game'

interface Props {
  stats: Stats
  turn: number
  maxTurns: number
}

interface BarProps {
  label: string
  value: number
  color: string
  dangerBelow?: number
  dangerAbove?: number
}

function PixelBar({ label, value, color, dangerBelow, dangerAbove }: BarProps) {
  const isDanger =
    (dangerBelow !== undefined && value <= dangerBelow) ||
    (dangerAbove !== undefined && value >= dangerAbove)

  const segments = 10
  const filled = Math.round((value / 100) * segments)

  return (
    <div className="stat-row">
      <span className={`stat-label ${isDanger ? 'blink text-red' : ''}`}>{label}</span>
      <div className="pixel-bar-track">
        {Array.from({ length: segments }).map((_, i) => (
          <div
            key={i}
            className="pixel-bar-seg"
            style={{
              background: i < filled ? color : 'transparent',
              borderColor: isDanger ? '#ff0000' : color,
            }}
          />
        ))}
      </div>
      <span className={`stat-val ${isDanger ? 'text-red' : ''}`}>{value}</span>
    </div>
  )
}

export function StatsBar({ stats, turn, maxTurns }: Props) {
  const repColor = stats.reputation >= 0 ? '#00d4ff' : '#ff6b35'

  return (
    <div className="stats-panel pixel-box">
      <div className="stats-header">
        <span className="pixel-label">STATUS</span>
        <span className="turn-counter">TURN {turn}/{maxTurns}</span>
      </div>
      <PixelBar
        label="양아치"
        value={stats.yangachi}
        color="#ff6b35"
        dangerAbove={90}
      />
      <PixelBar
        label="친절함"
        value={stats.kindness}
        color="#00ff41"
        dangerBelow={10}
      />
      <div className="stat-row">
        <span className="stat-label">평판</span>
        <span className="stat-val" style={{ color: repColor, fontSize: '0.7rem' }}>
          {stats.reputation > 0 ? `+${stats.reputation}` : stats.reputation}
        </span>
      </div>
    </div>
  )
}
