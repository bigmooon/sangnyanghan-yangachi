from contextlib import asynccontextmanager
import logging

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.config import get_settings

logger = logging.getLogger(__name__)


@asynccontextmanager
async def lifespan(app: FastAPI):
    settings = get_settings()

    if settings.use_langgraph:
        # ChromaDB + RAG 파이프라인 초기화
        try:
            from app.ai.llm.service import get_llm_service
            from app.ai.rag.pipeline import RAGPipeline, set_pipeline

            llm_service = get_llm_service()
            pipeline = RAGPipeline(
                host=settings.chromadb_host,
                port=settings.chromadb_port,
                embeddings=llm_service.get_embeddings(),
            )
            await pipeline.init_collections()
            set_pipeline(pipeline)

            if pipeline.is_available:
                logger.info("RAG 파이프라인 초기화 완료 (ChromaDB 연결됨)")
            else:
                logger.warning("ChromaDB 미연결 — RAG 없이 LLM만 사용")
        except Exception as e:
            logger.error("LLM/RAG 초기화 실패: %s — Phase 1 모드로 전환", e)

    yield

    logger.info("서버 종료")


def create_app() -> FastAPI:
    settings = get_settings()

    app = FastAPI(
        title=settings.app_name,
        version="0.2.0",
        lifespan=lifespan,
    )

    app.add_middleware(
        CORSMiddleware,
        allow_origins=settings.cors_origins,
        allow_methods=["GET", "POST", "DELETE"],
        allow_headers=["*"],
        allow_credentials=True,
    )

    from app.api import game

    app.include_router(game.router, prefix="/api/game")

    @app.get("/api/health")
    async def health():
        from app.rag.pipeline import get_pipeline

        pipeline = get_pipeline()
        return {
            "status": "ok",
            "version": "0.2.0",
            "langgraph": settings.use_langgraph,
            "rag": pipeline.is_available if pipeline else False,
        }

    return app


app = create_app()
