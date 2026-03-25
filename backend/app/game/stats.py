def clamp(value: int, min_val: int = 0, max_val: int = 100) -> int:
    return max(min_val, min(max_val, value))


def update_stats(session: dict, effects: dict) -> dict:
    """
    이벤트/아이템 효과 적용

    effects key: yangachi_raw, kindness_raw, reputation
    """
    yangachi_delta = effects.get("yangachi_raw", effects.get("yangachi", 0))
    kindness_delta = effects.get("kindness_raw", effects.get("kindness", 0))
    reputation_delta = effects.get("reputation", 0)

    return {
        **session,
        "yangachi_raw": session["yangachi_raw"] + yangachi_delta,
        "kindness_raw": session["kindness_raw"] + kindness_delta,
        "reputation": session["reputation"] + reputation_delta,
    }


def get_display_stats(session: dict) -> dict[str, int]:
    """API 응답용"""
    return {
        "yangachi": clamp(session["yangachi_raw"]),
        "kindness": clamp(session["kindness_raw"]),
        "reputation": session["reputation"],
    }
