import { BrowserRouter, Routes, Route, Navigate } from 'react-router-dom'
import { useState } from 'react'
import { MainMenu } from './pages/MainMenu'
import { CharacterSelect } from './pages/CharacterSelect'
import { GamePlay } from './pages/GamePlay'
import { RunReport } from './pages/RunReport'
import type { GameState } from './types/game'

export default function App() {
  const [activeGameState, setActiveGameState] = useState<GameState | null>(null)

  return (
    <BrowserRouter>
      <Routes>
        <Route path="/" element={<MainMenu />} />
        <Route
          path="/character-select"
          element={<CharacterSelect onGameStart={setActiveGameState} />}
        />
        <Route
          path="/game"
          element={
            activeGameState
              ? <GamePlay initialState={activeGameState} />
              : <Navigate to="/" replace />
          }
        />
        <Route path="/run-report" element={<RunReport />} />
        <Route path="*" element={<Navigate to="/" replace />} />
      </Routes>
    </BrowserRouter>
  )
}
