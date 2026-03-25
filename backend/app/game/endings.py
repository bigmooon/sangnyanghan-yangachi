from app.game.stats import clamp


def get_ending(session: dict) -> tuple[str, str]:
    yangachi = clamp(session["yangachi_raw"])
    kindness = clamp(session["kindness_raw"])
    reputation = session["reputation"]

    # 1. 완전한 양아치
    if yangachi >= 100:
        return (
            "full_yangachi",
            "축하한다! 네놈은 이제 이 구역의 살아있는 재앙이다. 마주치는 고양이조차 하악질을 멈추지 않는 고독한 폭군이 되었군. 켈켈켈!",
        )

    # 2. 무섭지만 존경받는 보스
    if yangachi >= 70 and reputation >= 20:
        return (
            "feared_but_respected",
            "오호, 공포의 군주 납셔! 다들 네 눈치 보느라 숨도 못 쉬지만, 의리 하나는 끝내주는군. 동네 꼬마들이 네 뒷모습만 봐도 90도로 인사한다!",
        )

    # 3. 진정한 상냥한 양아치 (best ending)
    if 40 <= yangachi <= 75 and kindness >= 55 and reputation >= 15:
        return (
            "true_kind_delinquent",
            "이것이 진정한 '상냥한 양아치'! 무서운 눈빛 뒤에 숨겨진 따뜻한 인류애가 폭발했다! 츤데레의 정점에 도달한 네놈에게 이 몸이 경의를 표하지.",
        )

    # 4. 성인군자
    if kindness >= 85 and yangachi <= 25:
        return (
            "saint",
            "양아치 때려치우고 절로 들어가라! 등 뒤에서 후광이 비쳐서 눈을 못 뜨겠군. 너 같은 녀석은 이 바닥의 수치다, 어서 성불이나 해버려!",
        )

    # 5. 동네에서 추방됨
    if reputation <= -15:
        return (
            "outcast",
            "사회적 말살 완료! 동네 편의점 알바가 네 얼굴을 보자마자 셔터를 내리고 경찰에 신고했다. 이제 이 구역에서 네 자리는 없다...",
        )

    # 6. 평범한 동네 형/누나
    if 30 <= yangachi <= 65 and 30 <= kindness <= 65:
        return (
            "balanced",
            "특색 없는 평범한 인간군상! 지루해서 하품이 다 나오는 결말이군. 양아치도 아니고 일반인도 아닌, 이도 저도 아닌 공기 같은 존재여!",
        )

    return (
        "survived",
        "질기기도 해라. 똥밭을 굴러도 이승이 좋다더니, 결국 꾸역꾸역 살아남았구나. 그 끈질긴 생명력만큼은 인정해주마. 켈켈켈!",
    )
