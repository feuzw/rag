"""FastAPI 서버 - LangChain RAG 시스템 API."""

import os
from typing import List, Optional

from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from langchain_openai import ChatOpenAI
import psycopg2
from sqlalchemy.exc import DataError

# 환경에 따라 상대/절대 import 선택
# 로컬: app/ 폴더가 있으면 상대 import 사용
# 우분투: app/ 폴더가 없고 루트에 파일들이 직접 있으면 절대 import 사용
try:
    from .app import get_vector_store, test_pgvector, wait_for_postgres
    from .models import (
        get_llm_provider,
        set_llm_provider,
        LLMProvider,
    )
    # ChatMidm은 선택적 import (우분투에서는 사용하지 않을 수 있음)
    try:
        from .models import ChatMidm
    except ImportError:
        ChatMidm = None
    from .router.rag_router import router as rag_router
    from .router.chat_router import router as chat_router
except ImportError:
    # 우분투 환경: 절대 import 사용
    from app import get_vector_store, test_pgvector, wait_for_postgres
    from models import (
        get_llm_provider,
        set_llm_provider,
        LLMProvider,
    )
    # ChatMidm은 선택적 import (우분투에서는 사용하지 않을 수 있음)
    try:
        from models import ChatMidm
    except ImportError:
        ChatMidm = None
    from router.rag_router import router as rag_router
    from router.chat_router import router as chat_router

app = FastAPI(title="LangChain RAG API", version="1.0.0")

# CORS 설정
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # 프로덕션에서는 특정 도메인으로 제한
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# 라우터 등록
app.include_router(rag_router)
app.include_router(chat_router)


# 요청/응답 모델
class SearchRequest(BaseModel):
    """검색 요청 모델."""

    query: str
    k: int = 5


class DocumentResponse(BaseModel):
    """문서 응답 모델."""

    content: str
    metadata: dict
    score: Optional[float] = None


class SearchResponse(BaseModel):
    """검색 응답 모델."""

    results: List[DocumentResponse]
    query: str
    total: int


class AddDocumentRequest(BaseModel):
    """문서 추가 요청 모델."""

    content: str
    metadata: Optional[dict] = None


class AddDocumentsRequest(BaseModel):
    """여러 문서 추가 요청 모델."""

    documents: List[AddDocumentRequest]


class ChatRequest(BaseModel):
    """채팅 요청 모델."""

    query: str


class ChatResponse(BaseModel):
    """채팅 응답 모델."""

    answer: str
    query: str
    model: str


class SearchAndChatResponse(BaseModel):
    """검색 및 채팅 통합 응답 모델."""

    answer: str
    sources: List[DocumentResponse]
    query: str


# 전역 변수
_vector_store = None
_llm_initialized = False


def get_vector_store_instance():
    """벡터 스토어 인스턴스를 가져옵니다."""
    global _vector_store
    if _vector_store is None:
        _vector_store = get_vector_store()
    return _vector_store


def _initialize_default_llm() -> ChatOpenAI:
    """기본 LLM을 초기화합니다.

    Returns:
        초기화된 ChatOpenAI 인스턴스.

    Raises:
        ValueError: OPENAI_API_KEY 환경 변수가 설정되지 않은 경우.
    """
    api_key = os.getenv("OPENAI_API_KEY")
    if not api_key:
        raise ValueError("OPENAI_API_KEY 환경 변수가 설정되지 않았습니다.")
    return ChatOpenAI(
        model="gpt-4o-mini",
        temperature=0.7,
        openai_api_key=api_key,
    )


@app.on_event("startup")
async def startup_event():
    """서버 시작 시 초기화."""
    print("🚀 FastAPI 서버 시작 중...")

    # Neon DB 또는 기타 PostgreSQL 연결 문자열 사용
    connection_string = os.getenv("POSTGRES_CONNECTION_STRING")

    if not connection_string:
        # 기본값으로 개별 환경 변수에서 조합 (하위 호환성)
        db_host = os.getenv("POSTGRES_HOST", "postgres")
        db_port = os.getenv("POSTGRES_PORT", "5432")
        db_user = os.getenv("POSTGRES_USER", "langchain")
        db_password = os.getenv("POSTGRES_PASSWORD", "langchain")
        db_name = os.getenv("POSTGRES_DB", "langchain")
        connection_string = (
            f"postgresql://{db_user}:{db_password}@{db_host}:{db_port}/{db_name}"
        )

    # PostgreSQL 연결 대기
    wait_for_postgres(connection_string)

    # pgvector 확장 확인
    test_pgvector(connection_string)

    # 벡터 스토어 초기화
    get_vector_store_instance()

    # LLM 프로바이더 초기화 (한번만 실행되도록 체크)
    global _llm_initialized
    if not _llm_initialized:
        provider = get_llm_provider()
        try:
            # 이미 주입된 LLM이 있는지 확인
            _ = provider.get_llm()
            print("✅ 주입된 LLM 사용 중")
            _llm_initialized = True
        except ValueError:
            # 환경 변수에서 LLM 프로바이더 확인
            llm_provider = os.getenv("LLM_PROVIDER", "openai").lower()

            if llm_provider == "midm":
                # Mi:dm 모델 사용
                if ChatMidm is None:
                    print("⚠️  ChatMidm을 import할 수 없습니다. OpenAI를 사용합니다.")
                    llm_provider = "openai"
                else:
                    try:
                        local_model_dir = os.getenv("LOCAL_MODEL_DIR")
                        midm_model = ChatMidm(
                            model_path=local_model_dir,  # None이면 기본 경로 사용
                            temperature=0.7,
                            max_tokens=512,
                        )
                        provider.set_llm(midm_model)
                        print(f"✅ Mi:dm 모델 초기화 완료! (경로: {local_model_dir or '기본 경로'})")
                        _llm_initialized = True
                    except Exception as e:
                        print(f"⚠️  Mi:dm 모델 초기화 실패: {e}")
                        print("   채팅 기능은 사용할 수 없지만 검색 기능은 정상 작동합니다.")

            # OpenAI 사용 (midm 실패 시 또는 기본값)
            if llm_provider != "midm" or ChatMidm is None or not _llm_initialized:
                # 기본 LLM (OpenAI) 초기화 시도
                try:
                    default_llm = _initialize_default_llm()
                    provider.set_llm(default_llm)
                    print("✅ 기본 LLM (OpenAI) 초기화 완료!")
                    _llm_initialized = True
                except ValueError as e:
                    print(f"⚠️  LLM 초기화 실패 (API 키 없음): {e}")
                    print("   채팅 기능은 사용할 수 없지만 검색 기능은 정상 작동합니다.")
                    print("   LLM을 주입하려면 set_llm_provider()를 사용하거나 환경 변수를 설정하세요.")
    else:
        print("✅ LLM은 이미 초기화되어 있습니다. (학습된 내용 보존)")

    print("✅ FastAPI 서버 준비 완료!")


@app.get("/")
async def root():
    """루트 엔드포인트."""
    return {"message": "LangChain RAG API", "status": "running"}


@app.get("/health")
async def health():
    """헬스 체크 엔드포인트."""
    return {"status": "healthy"}


@app.post("/search", response_model=SearchResponse)
async def search(request: SearchRequest):
    """유사도 검색을 수행합니다.

    Args:
        request: 검색 요청.

    Returns:
        검색 결과.
    """
    try:
        vector_store = get_vector_store_instance()
        results = vector_store.similarity_search_with_score(
            request.query, k=request.k
        )

        document_responses = [
            DocumentResponse(
                content=doc.page_content,
                metadata=doc.metadata,
                score=float(score),
            )
            for doc, score in results
        ]

        return SearchResponse(
            results=document_responses,
            query=request.query,
            total=len(document_responses),
        )
    except (DataError, psycopg2.errors.DataException) as e:
        error_msg = str(e)
        if "different vector dimensions" in error_msg:
            raise HTTPException(
                status_code=400,
                detail=(
                    "벡터 차원 불일치 오류: 저장된 벡터와 현재 사용 중인 임베딩 모델의 차원이 다릅니다. "
                    "데이터베이스를 초기화하려면 /reset-collection 엔드포인트를 호출하세요."
                ),
            )
        raise HTTPException(status_code=500, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/add-document")
async def add_document(request: AddDocumentRequest):
    """단일 문서를 추가합니다.

    Args:
        request: 문서 추가 요청.

    Returns:
        추가 결과.
    """
    try:
        try:
            from .service.embedding_ingest_service import add_document as add_doc_service
        except ImportError:
            from service.embedding_ingest_service import add_document as add_doc_service
        return add_doc_service(request.content, request.metadata)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/add-documents")
async def add_documents(request: AddDocumentsRequest):
    """여러 문서를 추가합니다.

    Args:
        request: 문서 추가 요청.

    Returns:
        추가 결과.
    """
    try:
        try:
            from .service.embedding_ingest_service import add_documents as add_docs_service
        except ImportError:
            from service.embedding_ingest_service import add_documents as add_docs_service
        documents = [
            {"content": doc.content, "metadata": doc.metadata or {}}
            for doc in request.documents
        ]
        return add_docs_service(documents)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))




@app.post("/reset-collection")
async def reset_collection():
    """벡터 컬렉션을 초기화합니다.

    주의: 이 작업은 모든 저장된 문서를 삭제합니다.

    Returns:
        초기화 결과.
    """
    try:
        # Neon DB 또는 기타 PostgreSQL 연결 문자열 사용
        connection_string = os.getenv("POSTGRES_CONNECTION_STRING")

        if not connection_string:
            # 기본값으로 개별 환경 변수에서 조합 (하위 호환성)
            db_host = os.getenv("POSTGRES_HOST", "postgres")
            db_port = os.getenv("POSTGRES_PORT", "5432")
            db_user = os.getenv("POSTGRES_USER", "langchain")
            db_password = os.getenv("POSTGRES_PASSWORD", "langchain")
            db_name = os.getenv("POSTGRES_DB", "langchain")
            connection_string = (
                f"postgresql://{db_user}:{db_password}@{db_host}:{db_port}/{db_name}"
            )

        # PostgreSQL 연결
        conn = psycopg2.connect(connection_string)
        conn.autocommit = True
        cursor = conn.cursor()

        # langchain_pg_embedding 테이블의 모든 데이터 삭제
        cursor.execute("DELETE FROM langchain_pg_embedding;")
        deleted_count = cursor.rowcount

        # langchain_pg_collection 테이블의 모든 데이터 삭제
        cursor.execute("DELETE FROM langchain_pg_collection;")
        collection_count = cursor.rowcount

        cursor.close()
        conn.close()

        # 전역 변수 초기화
        global _vector_store
        _vector_store = None

        return {
            "message": "컬렉션이 성공적으로 초기화되었습니다.",
            "status": "success",
            "deleted_embeddings": deleted_count,
            "deleted_collections": collection_count,
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"컬렉션 초기화 실패: {str(e)}")


if __name__ == "__main__":
    import uvicorn

    uvicorn.run(app, host="0.0.0.0", port=8000)

