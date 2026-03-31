from typing import Literal

from pydantic import BaseModel, Field


class Character(BaseModel):
    id: int
    name: str
    description: str


class Stats(BaseModel):
    yangachi: int = Field(ge=0, le=100, description="양아치력 (0~100)")
    kindness: int = Field(ge=0, le=100, description="친절 (0~100)")
    reputation: int = Field(description="평판")


class Item(BaseModel):
    id: str
    name: str
    icon: str
    description: str = ""


class RunReport(BaseModel):
    summary: str
    highlights: list[str] = []
    character_arc: str = ""
    final_assessment: str = ""
    star_rating: int = 3


class GameState(BaseModel):
    session_id: str
    turn: int
    max_turns: int
    character: Character
    stats: Stats
    inventory: list[Item]
    current_event_title: str | None = None
    current_choices: dict[str, str] | None = (
        None  # {"A": "...", "B": "...", "C": "..."}
    )
    is_game_over: bool
    game_over_reason: str | None = None
    ending_type: str | None = None
    # Phase 2: LLM 생성 필드 (없으면 None)
    narrative: str | None = None
    run_report: RunReport | None = None


# POST /api/game/start
class StartGameRequest(BaseModel):
    character_id: int = Field(ge=1, le=3, description="캐릭터 ID (1~3)")


class StartGameResponse(BaseModel):
    session_id: str
    character: Character
    state: GameState


# POST /api/game/choice
class SubmitChoiceRequest(BaseModel):
    session_id: str
    choice: Literal["A", "B", "C"]


class SubmitChoiceResponse(BaseModel):
    state: GameState
    result_message: str = Field(description="선택 결과 텍스트")
    side_effect_message: str | None = None
    result_narration: str | None = None  # LLM 생성 결과 내러티브


# POST /api/game/item
class UseItemRequest(BaseModel):
    session_id: str
    item_id: str


class UseItemResponse(BaseModel):
    state: GameState
    message: str = Field(description="아이템 사용 결과 텍스트")


# GET /api/game/state/{session_id}
class GameStateResponse(BaseModel):
    state: GameState


# POST /api/game/next
class NextEventRequest(BaseModel):
    session_id: str


# DELETE /api/game/session
class EndGameRequest(BaseModel):
    session_id: str


class EndGameResponse(BaseModel):
    ending_message: str
