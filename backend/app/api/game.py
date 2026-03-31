import asyncio
from typing import Any
import uuid

from fastapi import APIRouter, HTTPException, Query
from langgraph.types import Command
from sse_starlette.sse import EventSourceResponse

from app.api.schemas import (
    Character,
    EndGameRequest,
    EndGameResponse,
    GameState as GameStateSchema,
    GameStateResponse,
    Item,
    NextEventRequest,
    RunReport as RunReportSchema,
    StartGameRequest,
    StartGameResponse,
    Stats,
    SubmitChoiceRequest,
    SubmitChoiceResponse,
    UseItemRequest,
    UseItemResponse,
)
from app.config import get_settings
from app.data.loader import get_characters, get_events, get_items
from app.game import (
    process_choice as engine_process_choice,
    select_event,
    use_item as engine_use_item,
)
from app.graph.builder import get_game_graph

router = APIRouter(tags=["game"])

MAX_TURNS = 10

_sessions: dict[str, dict] = {}


def _items_data() -> dict[str, dict]:
    return get_items()


def _session_to_schema(session_id: str, s: dict) -> GameStateSchema:
    """세션 dict(Phase 1) 또는 LangGraph state dict → GameStateSchema"""
    items_data = _items_data()
    character_data = s["character"]
    return GameStateSchema(
        session_id=session_id,
        turn=s["turn"],
        max_turns=s["max_turns"],
        character=Character(
            id=character_data["id"],
            name=character_data["name"],
            description=character_data["description"],
        ),
        stats=Stats(
            yangachi=max(0, min(100, s["yangachi_raw"])),
            kindness=max(0, min(100, s["kindness_raw"])),
            reputation=s["reputation"],
        ),
        inventory=[
            Item(
                id=iid,
                name=items_data[iid]["name"],
                icon=items_data[iid]["icon"],
            )
            for iid in s.get("inventory", [])
            if iid in items_data
        ],
        current_event_title=s.get("current_event_title"),
        current_choices=s.get("current_choices"),
        is_game_over=s.get("is_game_over", False),
        game_over_reason=s.get("game_over_reason"),
        ending_type=s.get("ending_type"),
        narrative=s.get("narrative"),
        run_report=(
            RunReportSchema(**s["run_report"]) if s.get("run_report") else None
        ),
    )


def _langgraph_config(session_id: str) -> dict:
    return {"configurable": {"thread_id": session_id}}


def _get_langgraph_state(session_id: str) -> dict:
    graph = get_game_graph()
    snapshot = graph.get_state(_langgraph_config(session_id))
    if snapshot is None or not snapshot.values:
        raise HTTPException(
            status_code=404, detail=f"세션을 찾을 수 없습니다: {session_id}"
        )
    return snapshot.values


def _build_initial_state(session_id: str, character_data: dict) -> dict:
    initial = character_data["initial_state"]
    return {
        "session_id": session_id,
        "character": character_data,
        "turn": 1,
        "max_turns": MAX_TURNS,
        "yangachi_raw": initial["yangachi"],
        "kindness_raw": initial["kindness"],
        "reputation": initial["reputation"],
        "inventory": [],
        "used_event_ids": [],
        "current_event_title": None,
        "current_choices": None,
        "current_choices_data": None,
        "player_choice": None,
        "event_history": [],
        "choice_history": [],
        "is_game_over": False,
        "game_over_reason": None,
        "ending_type": None,
        "game_over_shield": False,
        "mitigate_next_choice": None,
        "narrative": None,
        "result_narration": None,
        "side_effect_message": None,
        "run_report": None,
    }


# ---------------------------------------------------------------------------
# POST /api/game/start
# ---------------------------------------------------------------------------


@router.post("/start", response_model=StartGameResponse, summary="게임 시작")
async def start_game(body: StartGameRequest) -> StartGameResponse:
    characters = get_characters()
    character_data = characters.get(body.character_id)
    if not character_data:
        raise HTTPException(
            status_code=400, detail=f"유효하지 않은 캐릭터 ID: {body.character_id}"
        )

    session_id = str(uuid.uuid4())
    settings = get_settings()

    if settings.use_langgraph:
        initial_state = _build_initial_state(session_id, character_data)
        graph = get_game_graph()
        config = _langgraph_config(session_id)
        # generate_event까지 실행 후 process_choice의 interrupt()에서 멈춤
        final_state = await graph.ainvoke(initial_state, config)
        state_schema = _session_to_schema(session_id, final_state)
    else:
        # Phase 1 fallback
        initial: dict[str, Any] = {
            "character": character_data,
            "turn": 1,
            "max_turns": MAX_TURNS,
            "yangachi_raw": character_data["initial_state"]["yangachi"],
            "kindness_raw": character_data["initial_state"]["kindness"],
            "reputation": character_data["initial_state"]["reputation"],
            "inventory": [],
            "used_event_ids": [],
            "current_event_title": None,
            "current_choices": None,
            "current_choices_data": None,
            "is_game_over": False,
            "game_over_reason": None,
            "ending_type": None,
            "game_over_shield": False,
            "mitigate_next_choice": None,
        }
        session_with_event, _ = select_event(initial, get_events())
        _sessions[session_id] = session_with_event
        state_schema = _session_to_schema(session_id, _sessions[session_id])

    return StartGameResponse(
        session_id=session_id,
        character=state_schema.character,
        state=state_schema,
    )


# ---------------------------------------------------------------------------
# GET /api/game/state
# ---------------------------------------------------------------------------


@router.get("/state", response_model=GameStateResponse, summary="현재 상태 조회")
async def get_game_state(session_id: str = Query(...)) -> GameStateResponse:
    settings = get_settings()
    if settings.use_langgraph:
        state = _get_langgraph_state(session_id)
    else:
        if session_id not in _sessions:
            raise HTTPException(
                status_code=404, detail=f"세션을 찾을 수 없습니다: {session_id}"
            )
        state = _sessions[session_id]
    return GameStateResponse(state=_session_to_schema(session_id, state))


# ---------------------------------------------------------------------------
# POST /api/game/choice
# ---------------------------------------------------------------------------


@router.post("/choice", response_model=SubmitChoiceResponse, summary="선택지 제출")
async def submit_choice(body: SubmitChoiceRequest) -> SubmitChoiceResponse:
    settings = get_settings()

    if settings.use_langgraph:
        try:
            current = _get_langgraph_state(body.session_id)
        except HTTPException:
            raise

        if current.get("is_game_over"):
            raise HTTPException(status_code=400, detail="이미 종료된 게임입니다.")

        graph = get_game_graph()
        config = _langgraph_config(body.session_id)
        # interrupt()가 대기 중인 process_choice를 resume
        new_state = await graph.ainvoke(Command(resume=body.choice), config)

        return SubmitChoiceResponse(
            state=_session_to_schema(body.session_id, new_state),
            result_message=new_state.get("result_narration") or "",
            side_effect_message=new_state.get("side_effect_message"),
            result_narration=new_state.get("result_narration"),
        )

    # Phase 1 fallback
    session = _sessions.get(body.session_id)
    if not session:
        raise HTTPException(
            status_code=404, detail=f"세션을 찾을 수 없습니다: {body.session_id}"
        )
    if session["is_game_over"]:
        raise HTTPException(status_code=400, detail="이미 종료된 게임입니다.")

    try:
        new_session, result_message, side_effect_message = engine_process_choice(
            session, body.choice, get_events(), _items_data()
        )
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e)) from e

    _sessions[body.session_id] = new_session
    return SubmitChoiceResponse(
        state=_session_to_schema(body.session_id, new_session),
        result_message=result_message,
        side_effect_message=side_effect_message,
    )


# ---------------------------------------------------------------------------
# POST /api/game/item
# ---------------------------------------------------------------------------


@router.post("/item", response_model=UseItemResponse, summary="아이템 사용")
async def use_item_endpoint(body: UseItemRequest) -> UseItemResponse:
    items_data = _items_data()
    settings = get_settings()

    if settings.use_langgraph:
        current = _get_langgraph_state(body.session_id)
        if current.get("is_game_over"):
            raise HTTPException(status_code=400, detail="이미 종료된 게임입니다.")
        if body.item_id not in items_data:
            raise HTTPException(
                status_code=400, detail=f"유효하지 않은 아이템: {body.item_id}"
            )
        if body.item_id not in current.get("inventory", []):
            raise HTTPException(
                status_code=400, detail=f"인벤토리에 없는 아이템: {body.item_id}"
            )

        try:
            new_session, message = engine_use_item(current, body.item_id, items_data)
        except ValueError as e:
            raise HTTPException(status_code=400, detail=str(e)) from e

        # LangGraph 체크포인터 상태 직접 업데이트
        graph = get_game_graph()
        graph.update_state(_langgraph_config(body.session_id), new_session)
        return UseItemResponse(
            state=_session_to_schema(body.session_id, new_session), message=message
        )

    # Phase 1 fallback
    session = _sessions.get(body.session_id)
    if not session:
        raise HTTPException(
            status_code=404, detail=f"세션을 찾을 수 없습니다: {body.session_id}"
        )
    if session["is_game_over"]:
        raise HTTPException(status_code=400, detail="이미 종료된 게임입니다.")
    if body.item_id not in items_data:
        raise HTTPException(
            status_code=400, detail=f"유효하지 않은 아이템: {body.item_id}"
        )
    if body.item_id not in session["inventory"]:
        raise HTTPException(
            status_code=400, detail=f"인벤토리에 없는 아이템: {body.item_id}"
        )

    try:
        new_session, message = engine_use_item(session, body.item_id, items_data)
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e)) from e

    _sessions[body.session_id] = new_session
    return UseItemResponse(
        state=_session_to_schema(body.session_id, new_session), message=message
    )


# ---------------------------------------------------------------------------
# POST /api/game/next — 결과 확인 후 다음 이벤트로 진행
# ---------------------------------------------------------------------------


@router.post("/next", response_model=StartGameResponse, summary="다음 이벤트로 진행")
async def next_event(body: NextEventRequest) -> StartGameResponse:
    settings = get_settings()
    if not settings.use_langgraph:
        raise HTTPException(
            status_code=400, detail="LangGraph 모드에서만 사용 가능합니다."
        )

    try:
        current = _get_langgraph_state(body.session_id)
    except HTTPException:
        raise

    if current.get("is_game_over"):
        raise HTTPException(status_code=400, detail="이미 종료된 게임입니다.")

    graph = get_game_graph()
    config = _langgraph_config(body.session_id)
    new_state = await graph.ainvoke(Command(resume="next"), config)
    state_schema = _session_to_schema(body.session_id, new_state)
    return StartGameResponse(
        session_id=body.session_id,
        character=state_schema.character,
        state=state_schema,
    )


# ---------------------------------------------------------------------------
# DELETE /api/game/session
# ---------------------------------------------------------------------------


@router.delete("/session", response_model=EndGameResponse, summary="세션 종료")
async def end_game(body: EndGameRequest) -> EndGameResponse:
    settings = get_settings()
    if settings.use_langgraph:
        try:
            _get_langgraph_state(body.session_id)
        except HTTPException:
            raise
        # MemorySaver는 삭제 API가 없으므로 상태만 확인 후 응답
    else:
        if body.session_id not in _sessions:
            raise HTTPException(
                status_code=404, detail=f"세션을 찾을 수 없습니다: {body.session_id}"
            )
        del _sessions[body.session_id]

    return EndGameResponse(ending_message=f"세션이 종료되었습니다: {body.session_id}")


# ---------------------------------------------------------------------------
# GET /api/game/stream — SSE 내러티브 스트리밍 (typewriter 효과)
# ---------------------------------------------------------------------------


@router.get("/stream", summary="내러티브 SSE 스트림")
async def stream_narrative(session_id: str = Query(...)):
    """
    저장된 narrative를 문자 단위로 SSE 스트리밍한다.
    LLM을 재호출하지 않고 상태에 저장된 텍스트를 재생한다.
    """
    settings = get_settings()

    if settings.use_langgraph:
        try:
            state = _get_langgraph_state(session_id)
        except HTTPException as e:
            raise e
        narrative = state.get("narrative") or ""
    else:
        session = _sessions.get(session_id)
        if not session:
            raise HTTPException(
                status_code=404, detail=f"세션을 찾을 수 없습니다: {session_id}"
            )
        narrative = session.get("narrative") or session.get("current_event_title", "")

    async def event_generator():
        for char in narrative:
            yield {"data": char}
            await asyncio.sleep(0.02)
        yield {"event": "done", "data": ""}

    return EventSourceResponse(event_generator())
