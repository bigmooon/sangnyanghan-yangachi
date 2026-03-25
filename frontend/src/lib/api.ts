import type {
  StartGameResponse,
  SubmitChoiceResponse,
  UseItemResponse,
  EndGameResponse,
} from '../types/game'

const BASE = '/api/game'

async function request<T>(path: string, options?: RequestInit): Promise<T> {
  const res = await fetch(`${BASE}${path}`, {
    headers: { 'Content-Type': 'application/json' },
    ...options,
  })
  if (!res.ok) {
    const err = await res.json().catch(() => ({ detail: res.statusText }))
    throw new Error(err.detail ?? 'Request failed')
  }
  return res.json() as Promise<T>
}

export const api = {
  startGame: (character_id: number) =>
    request<StartGameResponse>('/start', {
      method: 'POST',
      body: JSON.stringify({ character_id }),
    }),

  getState: (session_id: string) =>
    request<{ state: import('../types/game').GameState }>(`/state?session_id=${session_id}`),

  submitChoice: (session_id: string, choice: 'A' | 'B' | 'C') =>
    request<SubmitChoiceResponse>('/choice', {
      method: 'POST',
      body: JSON.stringify({ session_id, choice }),
    }),

  useItem: (session_id: string, item_id: string) =>
    request<UseItemResponse>('/item', {
      method: 'POST',
      body: JSON.stringify({ session_id, item_id }),
    }),

  endGame: (session_id: string) =>
    request<EndGameResponse>('/session', {
      method: 'DELETE',
      body: JSON.stringify({ session_id }),
    }),
}
