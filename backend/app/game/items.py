from app.game.stats import update_stats

MAX_INVENTORY = 5


def has_item(session: dict, item_id: str) -> bool:
    return item_id in session["inventory"]


def add_item(session: dict, item_id: str) -> tuple[dict, bool]:
    if len(session["inventory"]) >= MAX_INVENTORY:
        return session, False

    if item_id in session["inventory"]:
        return session, False

    return {**session, "inventory": [*session["inventory"], item_id]}, True


def remove_item(session: dict, item_id: str) -> dict:
    inventory = [i for i in session["inventory"] if i != item_id]
    return {**session, "inventory": inventory}


def apply_item(session: dict, item_id: str, items_data: dict) -> tuple[dict, str]:
    """
    아이템 사용. 동작 방식은 items.json의 필드로 결정된다:
    - special == "shield" → game_over_shield 활성화
    - mitigate 필드 존재 → mitigate_next_choice 플래그 설정
    - 그 외 → effect 즉시 적용

    Returns:
        tuple[dict, str]: (new_session, result_message)
    """
    if not has_item(session, item_id):
        raise ValueError(f"인벤토리에 없는 아이템: {item_id}")

    item = items_data[item_id]
    item_name = item["name"]
    effect = item.get("effect", {})

    new_session = remove_item(session, item_id)

    # shield → 게임오버 방지
    if item.get("special") == "shield":
        new_session = {**new_session, "game_over_shield": True}
        return (
            new_session,
            f"[{item_name}] 장착! '어이, 아직 내가 쓰러질 때가 아니라고?' 위기의 순간, 저승사자의 멱살을 잡고 한 번 돌아옵니다.",
        )

    # mitigate → 스탯 변화 완화
    if item.get("mitigate"):
        new_session = {**new_session, "mitigate_next_choice": item["mitigate"]}
        return (
            new_session,
            f"[{item_name}] 복용 완료. 뇌가 멍해지며 세상의 시선이 두렵지 않게 됩니다. 다음 선택에서 올 스탯 변화가 무뎌집니다.",
        )

    # 기본: effect 즉시 적용
    new_session = update_stats(new_session, effect)

    parts = []
    yangachi_delta = effect.get("yangachi", 0)
    kindness_delta = effect.get("kindness", 0)
    if yangachi_delta > 0:
        parts.append(f"양아치력 +{yangachi_delta}")
    elif yangachi_delta < 0:
        parts.append(f"양아치력 {yangachi_delta}")
    if kindness_delta > 0:
        parts.append(f"친절함 +{kindness_delta}")
    elif kindness_delta < 0:
        parts.append(f"친절함 {kindness_delta}")

    effect_text = ", ".join(parts) if parts else "변화 없음"

    return (
        new_session,
        f"[{item_name}]을(를) 사용했다! 몸 안에서 정체 모를 힘이 샘솟는다... ({effect_text})",
    )
