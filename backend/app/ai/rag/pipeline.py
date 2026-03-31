from pathlib import Path

import chromadb
from langchain_chroma import Chroma
from langchain_core.documents import Document
from langchain_core.embeddings import Embeddings

from app.data.loader import get_events


class RAGPipeline:
    """
    ChromaDB 클라이언트 내장 RAG 파이프라인
    """

    def __init__(self, host: str, port: int, embeddings: Embeddings):
        self._embeddings = embeddings
        try:
            self._client = chromadb.HttpClient(host=host, port=port)
            self._client.heartbeat()
            self.is_available = True
        except Exception as e:
            print(f"ChromaDB 연결 실패: {e}")
            self.is_available = False

    def _get_vector_store(self, collection_name: str) -> Chroma:
        return Chroma(
            client=self._client,
            collection_name=collection_name,
            embedding_function=self._embeddings,
        )

    async def init_collections(self) -> None:
        """
        컬렉션 초기화 및 초기 대이터 로드
        """
        if not self.is_available:
            return

        # 세계관 데이터
        bible_path = Path(__file__).parent.parent / "data" / "bible.md"
        if bible_path.exists():
            content = bible_path.read_text(encoding="utf-8")
            chunks = [p.strip() for p in content.split("\n\n") if p.strip()]
            docs = [
                Document(page_contents=c, metadata={"source": "bible"}) for c in chunks
            ]

            # 데이터 없으면 추가
            store = self._get_vector_store("bible")
            if store._collection.count() == 0:
                store.add_documents(docs)

        # 이벤트 템플릿 데이터
        events = get_events()
        event_docs = [
            Document(
                page_content=f"{e['title']}\n{e['description']}",
                metadata={"event_id": e["id"]},
            )
            for e in events
        ]
        event_store = self._get_vector_store("event_templates")
        if event_store._collection.count() == 0:
            event_store.add_documents(event_docs)

        print("RAG Pipeline 준비 완료")

    def add_session_event(
        self,
        session_id: str,
        turn: int,
        event_title: str,
        choice_text: str,
        result: str,
    ):
        """
        플레이 기록 저장
        """
        if not self.is_available:
            return

        content = f"턴{turn}: {event_title} -> {choice_text} -> {result}"
        doc = Document(
            page_content=content, metadata={"session_id": session_id, "turn": turn}
        )
        self._get_vector_store("game_sessions").add_documents([doc])

    def get_bible_context(self, query: str, k: int = 3) -> str:
        """
        세계관 설정 검색
        """
        if not self.is_available:
            return ""

        docs = self._get_vector_store("bible").similarity_search(query, k=k)
        return "\n\n".join(d.page_content for d in docs)

    def get_session_history(self, session_id: str, k: int = 5) -> str:
        """
        메타데이터 필터링 -> 세션 기록 검색
        """
        if not self.is_available:
            return ""

        store = self._get_vector_store("game_sessions")
        docs = store.similarity_search(query="", k=k, filter={"session_id": session_id})
        # 턴 순서대로 정렬
        sorted_docs = sorted(docs, key=lambda x: x.metadata.get("turn", 0))
        return "\n".join(d.page_content for d in sorted_docs)


_pipeline: RAGPipeline | None = None


def set_pipeline(pipeline: RAGPipeline):
    global _pipeline
    _pipeline = pipeline


def get_pipeline() -> RAGPipeline | None:
    return _pipeline
