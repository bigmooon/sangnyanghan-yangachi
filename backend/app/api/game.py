import json
from pathlib import Path
from typing import Any
import uuid

from fastapi import APIRouter, HTTPException, Query

from app.api.schemas import (
    Character,
    EndGameRequest,
    EndGameResponse,
    GameState,
    GameStateResponse,
    Item,
    StartGameRequest,
    StartGameResponse,
    Stats,
    SubmitChoiceRequest,
    SubmitChoiceResponse,
    UseItemRequest,
    UseItemResponse,
)

router = APIRouter(tags=["game"])

_DATA_DIR = Path(__file__).parent.parent / "data"

MAX_TURNS = 10


def _load_json(filename: str) -> Any:
    safe_path = (_DATA_DIR / filename).resolve()
    if not str(safe_path).startswith(str(_DATA_DIR.resolve())):
        raise ValueError(f"Invalid filename: {filename}")
    with safe_path.open(encoding="utf-8") as f:
        return json.load(f)


try:
    _CHARACTERS: dict[int, dict] = {
        character["id"]: character
        for character in _load_json("characters.json")["characters"]
    }
    _ITEMS: dict[str, dict] = _load_json("items.json")["items"]
except (FileNotFoundError, json.JSONDecodeError, KeyError) as e:
    raise RuntimeError(f"게임 데이터 로드 실패: {e}") from e

# TODO: 추후 LangGraph checkpointer로 교체
_sessions: dict[str, dict] = {}


def _get_session(session_id: str) -> dict:
    session = _sessions.get(session_id)
    if not session:
        raise HTTPException(
            status_code=404, detail=f"세션을 찾을 수 없습니다: {session_id}"
        )
    return session


def _get_state(session_id: str, session: dict) -> GameState:
    character_data = session["character"]
    return GameState(
        session_id=session_id,
        turn=session["turn"],
        max_turns=session["max_turns"],
        character=Character(
            id=character_data["id"],
            name=character_data["name"],
            description=character_data["description"],
        ),
        stats=Stats(
            yangachi=max(0, min(100, session["yangachi_raw"])),
            kindness=max(0, min(100, session["kindness_raw"])),
            reputation=session["reputation"],
        ),
        inventory=[
            Item(
                id=item_id,
                name=_ITEMS[item_id]["name"],
                icon=_ITEMS[item_id]["icon"],
            )
            for item_id in session["inventory"]
            if item_id in _ITEMS
        ],
        current_event_title=session.get("current_event_title"),
        current_choices=session.get("current_choices"),
        is_game_over=session["is_game_over"],
        game_over_reason=session.get("game_over_reason"),
        ending_type=session.get("ending_type"),
    )


# POST /api/game/start
@router.post("/start", response_model=StartGameResponse, summary="게임 시작")
async def start_game(body: StartGameRequest) -> StartGameResponse:
    """게임 시작 및 캐릭터 선택"""
    character_data = _CHARACTERS.get(body.character_id)
    if not character_data:
        raise HTTPException(
            status_code=400, detail=f"유효하지 않은 캐릭터 ID: {body.character_id}"
        )

    session_id = str(uuid.uuid4())
    initial = character_data["initial_state"]

    _sessions[session_id] = {
        "character": character_data,
        "turn": 1,
        "max_turns": MAX_TURNS,
        "yangachi_raw": initial["yangachi"],
        "kindness_raw": initial["kindness"],
        "reputation": initial["reputation"],
        "inventory": [],
        "current_event_title": None,
        "current_choices": None,
        "is_game_over": False,
        "game_over_reason": None,
        "ending_type": None,
    }

    state = _get_state(session_id, _sessions[session_id])
    return StartGameResponse(
        session_id=session_id,
        character=state.character,
        state=state,
    )


# GET /api/game/state
@router.get("/state", response_model=GameStateResponse, summary="현재 상태 조회")
async def get_game_state(
    session_id: str = Query(..., description="세션 ID"),
) -> GameStateResponse:
    session = _get_session(session_id)
    return GameStateResponse(state=_get_state(session_id, session))


# POST /api/game/choice
@router.post("/choice", response_model=SubmitChoiceResponse, summary="선택지 제출")
async def submit_choice(body: SubmitChoiceRequest) -> SubmitChoiceResponse:
    """
    TODO: LangGraph 구현 후 완성
    플레이어 선택지 제출 처리
    """
    _get_session(body.session_id)
    raise HTTPException(status_code=501, detail="구현 예정 API입니다.")


# POST /api/game/item
@router.post("/item", response_model=UseItemResponse, summary="아이템 사용")
async def use_item(body: UseItemRequest) -> UseItemResponse:
    """
    TODO: LangGraph 구현 후 완성
    아이템 사용 처리
    """
    _get_session(body.session_id)
    if body.item_id not in _ITEMS:
        raise HTTPException(
            status_code=400, detail=f"유효하지 않은 아이템: {body.item_id}"
        )
    raise HTTPException(status_code=501, detail="구현 예정 API입니다.")


# DELETE /api/game/session
@router.delete("/session", response_model=EndGameResponse, summary="세션 종료")
async def end_game(body: EndGameRequest) -> EndGameResponse:
    """세션 종료 처리 및 상태 초기화"""
    _get_session(body.session_id)
    del _sessions[body.session_id]
    return EndGameResponse(ending_message=f"세션이 종료되었습니다: {body.session_id}")
