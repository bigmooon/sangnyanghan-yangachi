import json

from langchain_core.language_models import BaseChatModel
from langchain_core.output_parsers import StrOutputParser

from app.ai.llm.prompts import CHOICE_RESULT_PROMPT, EVENT_PROMPT, RUN_REPORT_PROMPT
from app.ai.llm.schemas import RunReport


def _extract_json(raw: str, field: str, fallback: str) -> str:
    """
    LLM 출력에서 JSON 필드 추출, 실패 시 fallback
    """
    try:
        start = raw.find("{")
        end = raw.rfind("}") + 1
        if start != -1 and end > start:
            data = json.loads(raw[start:end])
            return str(data.get(field, fallback))
    except Exception:
        pass

    return fallback


async def gen_event_story(llm: BaseChatModel, **kwargs) -> str:
    """
    1. 이벤트 내러티브생성
    """
    try:
        chain = EVENT_PROMPT | llm | StrOutputParser()
        raw = await chain.invoke(kwargs)
        return _extract_json(raw, "narrative", kwargs.get("event_description", ""))
    except Exception as e:
        print(f"[CHAINS] 이벤트 생성 실패: {e}")
        return kwargs.get("event_description", "")


async def gen_result_story(llm: BaseChatModel, **kwargs) -> str:
    """
    2. 선택 결과 내러티브 생성
    """
    try:
        chain = CHOICE_RESULT_PROMPT | llm | StrOutputParser()
        raw = await chain.invoke(kwargs)
        return _extract_json(raw, "narrative", kwargs.get("result_message", ""))
    except Exception as e:
        print(f"[CHAINS] 선택 결과 생성 실패: {e}")
        return kwargs.get("result_message", "")


async def gen_run_report(llm: BaseChatModel, **kwargs) -> RunReport:
    """
    3. 게임 결과 리포트 생성
    """
    try:
        chain = RUN_REPORT_PROMPT | llm | StrOutputParser()
        raw = await chain.invoke(kwargs)
        start = raw.find("{")
        end = raw.rfind("}") + 1
        if start != -1 and end > start:
            data = json.loads(raw[start:end])
            return RunReport(
                summary=data.get("summary", "여정이 끝났다."),
                highlights=data.get("highlights", []),
                character_arc=data.get("character_arc", ""),
                final_assessment=data.get("final_assessment", ""),
                star_rating=max(1, min(5, int(data.get("star_rating", 3)))),
            )
    except Exception as e:
        print(f"[CHAINS] 결과 리포트 생성 실패: {e}")

    return RunReport(
        summary=f"{kwargs.get('character_name', '')}의 여정이 끝났다.",
        highlights=[],
        character_arc="자신만의 길을 걸었다.",
        final_assessment=kwargs.get("game_over_reason", ""),
        star_rating=3,
    )
