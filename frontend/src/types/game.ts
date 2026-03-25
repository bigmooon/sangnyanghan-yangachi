export interface Character {
  id: number
  name: string
  description: string
}

export interface Stats {
  yangachi: number
  kindness: number
  reputation: number
}

export interface Item {
  id: string
  name: string
  icon: string
  description?: string
}

export interface GameState {
  session_id: string
  turn: number
  max_turns: number
  character: Character
  stats: Stats
  inventory: Item[]
  current_event_title: string | null
  current_choices: Record<string, string> | null
  is_game_over: boolean
  game_over_reason: string | null
  ending_type: string | null
}

export interface StartGameResponse {
  session_id: string
  character: Character
  state: GameState
}

export interface SubmitChoiceResponse {
  state: GameState
  result_message: string
  side_effect_message: string | null
}

export interface UseItemResponse {
  state: GameState
  message: string
}

export interface EndGameResponse {
  ending_message: string
}
