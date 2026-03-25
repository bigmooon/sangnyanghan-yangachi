interface Props {
  choices: Record<string, string>
  onChoice: (choice: 'A' | 'B' | 'C') => void
  disabled: boolean
}

const CHOICE_COLORS: Record<string, string> = {
  A: '#00ff41',
  B: '#00d4ff',
  C: '#ffd700',
}

export function ChoicePanel({ choices, onChoice, disabled }: Props) {
  return (
    <div className="choice-panel">
      <span className="pixel-label">▼ 선택하세요</span>
      <div className="choice-list">
        {Object.entries(choices).map(([key, text]) => (
          <button
            key={key}
            className="choice-btn"
            style={{ '--choice-color': CHOICE_COLORS[key] ?? '#ffffff' } as React.CSSProperties}
            onClick={() => onChoice(key as 'A' | 'B' | 'C')}
            disabled={disabled}
          >
            <span className="choice-key">[{key}]</span>
            <span className="choice-text">{text}</span>
          </button>
        ))}
      </div>
    </div>
  )
}
