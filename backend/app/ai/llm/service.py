import asyncio
from functools import lru_cache
import json

from langchain_ollama import ChatOllama
from langchain_openai import ChatOpenAI, OpenAIEmbeddings

from app.ai.llm.prompts import SLLM_PROMPT
from app.config import get_settings


class LLMService:
    def __init__(self) -> None:
        self._settings = get_settings()

    def get_chat_model(self):
        s = self._settings
        if s.llm_provider == "ollama":
            return ChatOllama(base_url=s.ollama_base_url, model=s.main_model)
        return ChatOpenAI(api_key=s.openai_api_key, model=s.main_model)

    def get_slm(self) -> ChatOllama:
        s = self._settings
        return ChatOllama(base_url=s.ollama_base_url, model=s.ollama_model)

    def get_embeddings(self) -> OpenAIEmbeddings:
        s = self._settings
        return OpenAIEmbeddings(api_key=s.openai_api_key, model=s.embed_model)


@lru_cache
def get_llm_service() -> LLMService:
    return LLMService()


async def slm_fine_tune_effects(
    effects: dict[str, int],
    current_stats: dict[str, int],
    context: str,
) -> dict[str, int]:
    """
    SLM으로 스탯 변화를 -20% ~ +20% 내에서 미세 조정
    """
    dy = effects.get("yangachi_raw", effects.get("yangachi", 0))
    dk = effects.get("kindness_raw", effects.get("kindness", 0))
    dr = effects.get("reputation", 0)

    # 변화 없을 시 SLM 호출 x
    if dy == 0 and dk == 0 and dr == 0:
        return effects

    prompt = SLLM_PROMPT.format(
        yangachi=current_stats.get("yangachi", 50),
        kindness=current_stats.get("kindness", 50),
        reputation=current_stats.get("reputation", 0),
        dy=dy,
        dk=dk,
        dr=dr,
        context=context[:300],
    )

    try:
        slm = get_llm_service().get_slm()
        response = await asyncio.wait_for(slm.invoke(prompt), timeout=5.9)
        raw = response.content if hasattr(response, "content") else str(response)

        # JSON 파싱
        start = raw.find("{")
        end = raw.rfind("}") + 1
        if start != -1 and end > start:
            data = json.loads(raw[start:end])
            return {
                "yangachi_raw": int(data.get("yangachi_delta", dy)),
                "kindness_raw": int(data.get("kindness_delta", dk)),
                "reputation": int(data.get("reputation_delta", dr)),
            }
    except TimeoutError as e:
        print(f"[SERVICE] SLM 타임아웃: {e}")
    except Exception as e:
        print(f"[SERVICE] SLM 호출 실패: {e}")

    return effects
