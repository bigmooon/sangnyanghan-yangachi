import logging

from langgraph.types import interrupt

from app.ai.llm.chains import (
    gen_event_story as generate_event_narrative,
    gen_result_story as generate_result_narration,
    gen_run_report as generate_run_report,
)
from app.ai.llm.service import get_llm_service, slm_fine_tune_effects
from app.ai.rag.pipeline import get_pipeline
from app.data.loader import get_events, get_items
from app.game.endings import get_ending
from app.game.engine import next_event
from app.game.game_over import has_game_over_shield, is_game_over, use_game_over_shield
from app.game.items import add_item
from app.game.stats import clamp, update_stats
from app.graph.state import GameState

logger = logging.getLogger(__name__)


def _display_stats(state: GameState) -> dict[str, int]:
    return {
        "yangachi": clamp(state["yangachi_raw"]),
        "kindness": clamp(state["kindness_raw"]),
        "reputation": state["reputation"],
    }


# 1. 캐릭터 선택
def character_select(state: GameState) -> dict:
    """
    character 필드에서 초기 스탯을 세팅한다.
    api/game.py의 start_game에서 initial_state를 받아 실행.
    """
    return {}  # initial_state에 이미 모든 값이 있으므로 pass-through


# 2. 이벤트 내러티브 생성
async def generate_event(state: GameState) -> dict:
    """
    정적 이벤트 풀에서 이벤트를 선택하고 LLM으로 내러티브를 생성한다.
    """
    new_session, event = next_event(state, get_events())

    # RAG 컨텍스트
    pipeline = get_pipeline()
    worldbuilding_ctx = ""
    event_history_text = ""
    if pipeline and pipeline.is_available:
        worldbuilding_ctx = pipeline.get_bible_context(event["title"])
        session_id = state.get("session_id", "")
        event_history_text = pipeline.get_session_history(session_id)

    # 히스토리 fallback (ChromaDB 없을 때)
    if not event_history_text:
        event_history_text = "\n".join(state.get("event_history", [])[-5:])

    # LLM 내러티브 생성
    character = state["character"]
    stats = _display_stats(state)
    narrative = await generate_event_narrative(
        get_llm_service().get_chat_model(),
        event_title=event["title"],
        event_description=event["description"],
        character_name=character["name"],
        character_description=character["description"],
        yangachi=stats["yangachi"],
        kindness=stats["kindness"],
        reputation=stats["reputation"],
        turn=state["turn"],
        max_turns=state["max_turns"],
        worldbuilding_context=worldbuilding_ctx,
        event_history=event_history_text,
    )

    return {
        "used_event_ids": new_session["used_event_ids"],
        "current_event_title": new_session["current_event_title"],
        "current_choices": new_session["current_choices"],
        "current_choices_data": new_session["current_choices_data"],
        "event_history": [*state.get("event_history", []), event["title"]],
        "narrative": narrative,
    }


# interrupt 포함 선택 대기
async def process_choice(state: GameState) -> dict:
    """
    interrupt()로 플레이어 입력을 기다린 뒤,
    규칙 엔진 → SLM 조정 → LLM 내러티브 순으로 처리한다.
    """
    # 선택 대기
    player_choice: str = interrupt(
        {
            "choices": state.get("current_choices", {}),
            "narrative": state.get("narrative"),
        }
    )

    choices_data: dict = state.get("current_choices_data") or {}
    if player_choice not in choices_data:
        raise ValueError(f"잘못된 선택: {player_choice}")

    choice_data = choices_data[player_choice]
    base_effects: dict = dict(choice_data.get("effects", {}))
    result_message: str = choice_data.get("result_message", "")
    item_drop: str | None = choice_data.get("item_drop")

    # 완화 아이템
    import math

    mitigate = state.get("mitigate_next_choice")
    if mitigate:
        base_effects = {k: math.floor(v * mitigate) for k, v in base_effects.items()}
        result_message = f"[정신 승리] {result_message}"

    # SLM 스탯 미세 조정 (비동기, 실패 시 fallback)
    stats = _display_stats(state)
    adjusted_effects = await slm_fine_tune_effects(
        base_effects,
        current_stats=stats,
        context=f"{state.get('current_event_title', '')} — {choice_data.get('text', '')}",
    )

    new_session = update_stats(state, adjusted_effects)
    if mitigate:
        new_session = {**new_session, "mitigate_next_choice": None}

    # 아이템 획득
    side_effect_msg: str | None = None
    items_data = get_items()
    if item_drop and item_drop in items_data:
        new_session, added = add_item(new_session, item_drop)
        if added:
            side_effect_msg = (
                f"오호, 길바닥에서 [{items_data[item_drop]['name']}]을(를) 주웠다!"
            )

    # 턴 증가
    new_turn = state["turn"] + 1

    # LLM 결과 내러티브
    pipeline = get_pipeline()
    wb_ctx = ""
    if pipeline and pipeline.is_available:
        wb_ctx = pipeline.get_bible_context(state.get("current_event_title", ""))

    dy = adjusted_effects.get("yangachi_raw", adjusted_effects.get("yangachi", 0))
    dk = adjusted_effects.get("kindness_raw", adjusted_effects.get("kindness", 0))
    dr = adjusted_effects.get("reputation", 0)

    result_narration = await generate_result_narration(
        get_llm_service().get_chat_model(),
        event_title=state.get("current_event_title", ""),
        player_choice_text=choice_data.get("text", player_choice),
        result_message=result_message,
        yangachi_delta=dy,
        kindness_delta=dk,
        reputation_delta=dr,
        worldbuilding_context=wb_ctx,
    )

    # RAG 기록 추가
    if pipeline and pipeline.is_available:
        pipeline.add_session_event(
            session_id=state.get("session_id", ""),
            turn=state["turn"],
            event_title=state.get("current_event_title", ""),
            choice_text=choice_data.get("text", player_choice),
            result=result_message,
        )

    # 히스토리 추가
    history_entry = {
        "turn": state["turn"],
        "event": state.get("current_event_title", ""),
        "choice": player_choice,
        "choice_text": choice_data.get("text", ""),
        "result": result_message,
        "effects": adjusted_effects,
    }

    return {
        **new_session,
        "turn": new_turn,
        "player_choice": player_choice,
        "result_narration": result_narration,
        "side_effect_message": side_effect_msg,
        "choice_history": [*state.get("choice_history", []), history_entry],
    }


# 3. 다음 버튼 대기
def await_next(state: GameState) -> dict:
    """
    결과 내러티브를 보여준 후 플레이어가 "다음" 버튼을 누를 때까지 대기한다.
    """
    interrupt("await_next")
    return {}


# 4. 게임오버 판정
def check_state(state: GameState) -> dict:
    """
    게임 오버 여부를 판단한다. 순수 Python 규칙만 사용.
    shield 처리도 여기서 수행.
    """
    is_over, reason = is_game_over(state)

    if not is_over:
        return {"is_game_over": False, "game_over_reason": None}

    # 게임오버 쉴드 처리
    if has_game_over_shield(state):
        new_state = use_game_over_shield(state)
        shield_msg = (
            "품속의 부적이 불타며 위기를 막아줬다! 아직은 죽을 때가 아닌 모양이군."
        )
        existing = new_state.get("side_effect_message")
        return {
            **new_state,
            "is_game_over": False,
            "game_over_reason": None,
            "side_effect_message": f"{existing} {shield_msg}".strip()
            if existing
            else shield_msg,
        }

    ending_type, ending_msg = get_ending(state)
    return {
        "is_game_over": True,
        "game_over_reason": reason,
        "ending_type": ending_type,
        "side_effect_message": ending_msg,
        "current_event_title": None,
        "current_choices": None,
        "current_choices_data": None,
    }


# 5. 게임 결과 생성(run report)
async def run_report(state: GameState) -> dict:
    """
    게임 종료 후 LLM으로 런 리포트를 생성한다.
    """
    character = state.get("character", {})
    stats = _display_stats(state)

    history_lines = []
    for entry in state.get("choice_history", []):
        history_lines.append(
            f"턴{entry['turn']}: {entry['event']} → {entry.get('choice_text', entry['choice'])}"
        )
    history_summary = "\n".join(history_lines)

    report = await generate_run_report(
        get_llm_service().get_chat_model(),
        character_name=character.get("name", ""),
        yangachi=stats["yangachi"],
        kindness=stats["kindness"],
        reputation=stats["reputation"],
        ending_type=state.get("ending_type", "survived"),
        game_over_reason=state.get("game_over_reason", ""),
        turns_played=state["turn"] - 1,
        max_turns=state["max_turns"],
        history_summary=history_summary,
    )

    return {"run_report": report.model_dump()}
