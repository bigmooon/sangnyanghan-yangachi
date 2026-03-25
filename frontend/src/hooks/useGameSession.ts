import { useState, useCallback } from 'react'
import { api } from '../lib/api'
import type { GameState } from '../types/game'

interface GameSessionState {
  gameState: GameState | null
  isLoading: boolean
  error: string | null
  resultMessage: string | null
  sideEffectMessage: string | null
}

export function useGameSession() {
  const [state, setState] = useState<GameSessionState>({
    gameState: null,
    isLoading: false,
    error: null,
    resultMessage: null,
    sideEffectMessage: null,
  })

  const clearMessages = useCallback(() => {
    setState(prev => ({ ...prev, resultMessage: null, sideEffectMessage: null, error: null }))
  }, [])

  const startGame = useCallback(async (character_id: number) => {
    setState(prev => ({ ...prev, isLoading: true, error: null }))
    try {
      const res = await api.startGame(character_id)
      setState(prev => ({ ...prev, isLoading: false, gameState: res.state }))
      return res.state
    } catch (e) {
      setState(prev => ({ ...prev, isLoading: false, error: (e as Error).message }))
      return null
    }
  }, [])

  const submitChoice = useCallback(async (choice: 'A' | 'B' | 'C') => {
    const sessionId = state.gameState?.session_id
    if (!sessionId) return

    setState(prev => ({ ...prev, isLoading: true, error: null }))
    try {
      const res = await api.submitChoice(sessionId, choice)
      setState(prev => ({
        ...prev,
        isLoading: false,
        gameState: res.state,
        resultMessage: res.result_message,
        sideEffectMessage: res.side_effect_message,
      }))
    } catch (e) {
      setState(prev => ({ ...prev, isLoading: false, error: (e as Error).message }))
    }
  }, [state.gameState?.session_id])

  const useItem = useCallback(async (item_id: string) => {
    const sessionId = state.gameState?.session_id
    if (!sessionId) return

    setState(prev => ({ ...prev, isLoading: true, error: null }))
    try {
      const res = await api.useItem(sessionId, item_id)
      setState(prev => ({
        ...prev,
        isLoading: false,
        gameState: res.state,
        resultMessage: res.message,
        sideEffectMessage: null,
      }))
    } catch (e) {
      setState(prev => ({ ...prev, isLoading: false, error: (e as Error).message }))
    }
  }, [state.gameState?.session_id])

  const endGame = useCallback(async () => {
    const sessionId = state.gameState?.session_id
    if (!sessionId) return null

    try {
      const res = await api.endGame(sessionId)
      return res.ending_message
    } catch {
      return null
    }
  }, [state.gameState?.session_id])

  const setGameState = useCallback((gs: GameState) => {
    setState(prev => ({ ...prev, gameState: gs }))
  }, [])

  return {
    ...state,
    startGame,
    submitChoice,
    useItem,
    endGame,
    setGameState,
    clearMessages,
  }
}
