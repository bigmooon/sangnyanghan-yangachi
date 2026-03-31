from typing import TypedDict


class GameState(TypedDict, total=False):
    session_id: str
    character: dict  # characters.json 항목 전체
    turn: int
    max_turns: int

    # 스탯
    yangachi_raw: int
    kindness_raw: int
    reputation: int

    # 인벤토리
    inventory: list[str]  # item_id 목록

    # 이벤트 플로우
    used_event_ids: list[str]
    current_event_title: str | None
    current_choices: dict[str, str] | None  # {"A": "...", ...}
    current_choices_data: dict[str, dict] | None  # 전체 선택지 데이터

    # 캐릭터 선택
    player_choice: str | None  # "A" | "B" | "C"

    # 로그
    event_history: list[str]  # 이벤트 제목 목록
    choice_history: list[dict]  # {turn, event, choice, result, effects}

    # 게임 오버
    is_game_over: bool
    game_over_reason: str | None
    ending_type: str | None

    # 아이템 효과
    game_over_shield: bool
    mitigate_next_choice: float | None

    # LLM 출력
    narrative: str | None
    result_narration: str | None
    side_effect_message: str | None
    run_report: dict | None
