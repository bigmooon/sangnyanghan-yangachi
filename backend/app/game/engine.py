import math
import random

from app.game.endings import get_ending
from app.game.game_over import has_game_over_shield, is_game_over, use_game_over_shield
from app.game.items import add_item, apply_item
from app.game.stats import update_stats


def next_event(session: dict, events_data: list[dict]) -> tuple[dict, dict]:
    """
    이벤트 풀에서 랜덤 이벤트 선택

    Returns:
        tuple[dict, dict]: (new_session, selected_event)
    """
    used_ids: list[str] = session.get("used_event_ids", [])
    available = [e for e in events_data if e["id"] not in used_ids]

    if not available:
        used_ids = []
        available = events_data

    event = random.choice(available)
    new_used_ids = [*used_ids, event["id"]]

    new_session = {
        **session,
        "used_event_ids": new_used_ids,
        "current_event_title": event["title"],
        "current_choices": {k: v["text"] for k, v in event["choices"].items()},
        "current_choices_data": event["choices"],
    }

    return new_session, event


def play_turn(
    session: dict, choice: str, events_data: list[dict], items_data: dict
) -> tuple[dict, str, str | None]:
    choices: dict = session.get("current_choices_data") or {}

    if choice not in choices:
        raise ValueError(f"어이, 없는 길을 가려고 하지 마라: {choice}")

    choice_data = choices[choice]
    effects = dict(choice_data.get("effects", {}))
    result_msg: str = choice_data.get("result_message", "")
    item_drop: str | None = choice_data.get("item_drop")

    # 완화 아이템 버프 적용
    mitigate = session.get("mitigate_next_choice")
    if mitigate:
        effects = {k: math.floor(v * mitigate) for k, v in effects.items()}
        result_msg = f"[정신 승리] {result_msg}"

    new_session = update_stats(session, effects)

    # 완화 플래그 소모
    if mitigate:
        new_session = {**new_session, "mitigate_next_choice": None}

    # 아이템 획득
    side_effect_msg: str | None = None
    if item_drop and item_drop in items_data:
        new_session, added = add_item(new_session, item_drop)
        if added:
            item_name = items_data[item_drop]["name"]
            side_effect_msg = f"오호, 길바닥에서 [{item_name}]을(를) 주웠다!"

    # 턴 증가
    new_session = {**new_session, "turn": new_session["turn"] + 1}

    # 게임오버 판정
    is_over, reason = is_game_over(new_session)

    if is_over:
        if has_game_over_shield(new_session):
            new_session = use_game_over_shield(new_session)
            shield_message = (
                "품속의 부적이 불타며 위기를 막아줬다! 아직은 죽을 때가 아닌 모양이군."
            )
            side_effect_msg = (
                f"{side_effect_msg} {shield_message}".strip()
                if side_effect_msg
                else shield_message
            )

            # 다음 이벤트 선택
            new_session, _ = next_event(new_session, events_data)
            return new_session, result_msg, side_effect_msg

        # 엔딩
        ending_type, ending_msg = get_ending(new_session)
        new_session = {
            **new_session,
            "is_game_over": True,
            "game_over_reason": reason,
            "ending_type": ending_type,
            "current_event_title": None,
            "current_choices": None,
            "current_choices_data": None,
        }
        side_effect_msg = (
            f"{side_effect_msg} | {ending_msg}" if side_effect_msg else ending_msg
        )
        return new_session, result_msg, side_effect_msg

    new_session, _ = next_event(new_session, events_data)
    return new_session, result_msg, side_effect_msg


def use_item(session: dict, item_id: str, items_data: dict) -> tuple[dict, str]:
    return apply_item(session, item_id, items_data)
