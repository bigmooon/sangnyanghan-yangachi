def is_game_over(session: dict) -> tuple[bool, str | None]:
    yangachi = session["yangachi_raw"]
    kindness = session["kindness_raw"]
    reputation = session["reputation"]

    if yangachi >= 100:
        return (
            True,
            "축하한다. 당신은 이제 완전무결한 양아치가 되었다. 이제 더 이상 '상냥함' 따위는 끼어들 틈이 없다. (배드 엔딩: 전설의 폭주족)",
        )

    if kindness <= 0:
        return (
            True,
            "심장의 온도가 영하로 떨어졌다. 타인을 향한 일말의 배려조차 남지 않은 당신은 이제 그저 걸어다니는 얼음 덩어리일 뿐이다.",
        )

    if reputation <= -20:
        return (
            True,
            "동네 편의점 알바조차 당신을 보면 문을 잠근다. 존재 자체가 민폐가 되어버린 당신에게 이 동네에 남은 자리는 없다.",
        )

    if yangachi <= 0 and kindness >= 100:
        return (
            True,
            "이럴 수가, 너무 착해진 나머지 등 뒤에서 후광이 비치기 시작했다. 당신은 이제 양아치가 아니라 '성인(Saint)'이다. (강제 성불 엔딩)",
        )

    if session["turn"] > session["max_turns"]:
        return (
            True,
            "어느덧 약속된 시간이 다 흘러갔다. 당신의 '상냥한 양아치' 수행기는 여기서 막을 내린다.",
        )

    return False, None


def has_game_over_shield(session: dict) -> bool:
    return session.get("game_over_shield", False)


def use_game_over_shield(session: dict) -> dict:
    return {**session, "game_over_shield": False}
