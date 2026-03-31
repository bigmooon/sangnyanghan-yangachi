from pydantic import BaseModel, Field


class EventChoice(BaseModel):
    text: str
    effect: dict[str, int] = Field(default_factory=dict)
    reputation_effect: int = 0
    item_reward: str | None = None


class GeneratedEvent(BaseModel):
    """LLM이 생성한 이벤트 내러티브"""

    narrative: str = Field(
        description="이벤트 상황을 묘사하는 풍부한 내러티브 (2~3문장)"
    )


class NarrationResult(BaseModel):
    """선택 결과에 대한 LLM 내러티브"""

    narration: str = Field(description="선택 결과를 묘사하는 풍부한 내러티브 (2~3문장)")


class SLMEffectAdjustment(BaseModel):
    """SLM이 조정한 스탯 변화량"""

    yangachi_delta: int = Field(description="양아치력 변화량")
    kindness_delta: int = Field(description="친절함 변화량")
    reputation_delta: int = Field(description="평판 변화량")


class RunReport(BaseModel):
    """게임 종료 후 LLM이 생성한 런 리포트"""

    summary: str = Field(description="한 줄 요약")
    highlights: list[str] = Field(default_factory=list, description="주요 장면 2~3개")
    character_arc: str = Field(description="캐릭터 성장/변화 서술")
    final_assessment: str = Field(description="최종 평가 멘트 (내레이터 말투)")
    star_rating: int = Field(ge=1, le=5, description="별점 1~5")
