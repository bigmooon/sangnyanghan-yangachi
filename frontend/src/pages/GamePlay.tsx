import { useNavigate } from 'react-router-dom'
import { useEffect, useState } from 'react'
import { useGameSession } from '../hooks/useGameSession'
import { StatsBar } from '../components/StatsBar'
import { ChoicePanel } from '../components/ChoicePanel'
import { InventoryPanel } from '../components/InventoryPanel'
import { GameOverModal } from '../components/GameOverModal'
import type { GameState } from '../types/game'

interface Props {
  initialState: GameState | null
}

export function GamePlay({ initialState }: Props) {
  const navigate = useNavigate()
  const {
    gameState,
    isLoading,
    error,
    resultMessage,
    sideEffectMessage,
    submitChoice,
    useItem,
    endGame,
    setGameState,
    clearMessages,
  } = useGameSession()

  const [showGameOver, setShowGameOver] = useState(false)


  useEffect(() => {
    if (initialState) {
      setGameState(initialState)
    } else {
      navigate('/')
    }
  }, [initialState, setGameState, navigate])

  useEffect(() => {
    if (gameState?.is_game_over && !showGameOver) {
      const timer = setTimeout(() => setShowGameOver(true), 800)
      return () => clearTimeout(timer)
    }
  }, [gameState?.is_game_over, showGameOver])

  const handleChoice = async (choice: 'A' | 'B' | 'C') => {
    clearMessages()
    await submitChoice(choice)
  }

  const handleUseItem = async (item_id: string) => {
    clearMessages()
    await useItem(item_id)
  }

  const handleContinueToReport = async () => {
    const endingMessage = await endGame()
    navigate('/run-report', { state: { gameState, endingMessage } })
  }

  if (!gameState) {
    return (
      <div className="screen">
        <div className="scanlines" />
        <div className="loading-screen">
          <p className="blink">LOADING...</p>
        </div>
      </div>
    )
  }

  const isDisabled = isLoading || gameState.is_game_over

  return (
    <div className="screen gameplay">
      <div className="scanlines" />

      <div className="game-layout">
        {/* Left sidebar */}
        <div className="game-sidebar">
          <StatsBar
            stats={gameState.stats}
            turn={gameState.turn}
            maxTurns={gameState.max_turns}
          />

          <div className="character-panel pixel-box">
            <span className="pixel-label">CHARACTER</span>
            <div className="char-info">
              <span className="char-name-display">{gameState.character.name}</span>
            </div>
          </div>

          <InventoryPanel
            inventory={gameState.inventory}
            onUseItem={handleUseItem}
            disabled={isDisabled}
          />
        </div>

        {/* Main game area */}
        <div className="game-main">
          {/* Event card */}
          <div className="event-card pixel-box">
            <div className="event-header">
              <span className="pixel-label text-cyan">
                ═══ EVENT ═══
              </span>
            </div>

            {gameState.current_event_title ? (
              <h3 className="event-title">{gameState.current_event_title}</h3>
            ) : (
              <p className="text-gray blink">이벤트 로딩 중...</p>
            )}
          </div>

          {/* Result messages */}
          {(resultMessage || sideEffectMessage || error) && (
            <div className="result-panel pixel-box">
              {resultMessage && (
                <p className="result-msg">
                  <span className="text-yellow">▶</span> {resultMessage}
                </p>
              )}
              {sideEffectMessage && (
                <p className="side-effect-msg blink">
                  <span className="text-red">⚠</span> {sideEffectMessage}
                </p>
              )}
              {error && (
                <p className="error-msg">
                  <span className="text-red">✗</span> {error}
                </p>
              )}
            </div>
          )}

          {/* Choices */}
          {gameState.current_choices && !gameState.is_game_over && (
            <ChoicePanel
              choices={gameState.current_choices}
              onChoice={handleChoice}
              disabled={isDisabled}
            />
          )}

          {isLoading && (
            <div className="loading-indicator">
              <span className="blink text-cyan">■ PROCESSING...</span>
            </div>
          )}
        </div>
      </div>

      {/* Game Over Modal */}
      {showGameOver && (
        <GameOverModal
          reason={gameState.game_over_reason}
          endingType={gameState.ending_type}
          onContinue={handleContinueToReport}
        />
      )}
    </div>
  )
}
