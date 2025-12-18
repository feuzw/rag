"""
FastAPI 기준의 API 엔드포인트 계층

rag_router.py
POST /api/rag

질문, 옵션(teamperature, k, etc)을 받고,
rag_service를 호출한 뒤 결과를 반환
"""

from typing import List, Optional
from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
import psycopg2
from sqlalchemy.exc import DataError

from ..service.rag_service import invoke_rag, search_with_rag
from ..models import get_llm

router = APIRouter(tags=["rag"])


class ChatRequest(BaseModel):
    """채팅 요청 모델."""

    query: str


class DocumentResponse(BaseModel):
    """문서 응답 모델."""

    content: str
    metadata: dict
    score: Optional[float] = None


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


@router.post("/chat", response_model=ChatResponse)
async def chat(request: ChatRequest):
    """RAG 기반 챗봇 응답을 생성합니다.

    Args:
        request: 챗봇 요청.

    Returns:
        챗봇 응답.
    """
    try:
        answer = invoke_rag(request.query)

        # LLM 타입 추출
        llm = get_llm()
        model_name = getattr(llm, "model_name", None) or getattr(llm, "model", None) or "unknown"

        return ChatResponse(
            answer=answer,
            query=request.query,
            model=str(model_name),
        )
    except ValueError as e:
        raise HTTPException(
            status_code=503,
            detail=f"LLM 서비스를 사용할 수 없습니다: {str(e)}"
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


@router.post("/rag", response_model=SearchAndChatResponse)
async def rag(request: ChatRequest):
    """검색 결과와 LLM 답변을 함께 반환합니다.

    Args:
        request: 챗봇 요청.

    Returns:
        검색 결과와 LLM 답변.
    """
    try:
        # 1. 벡터 검색 수행
        try:
            answer, search_results = search_with_rag(request.query, k=5)
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
            raise

        sources = [
            DocumentResponse(
                content=doc.page_content,
                metadata=doc.metadata,
                score=float(score),
            )
            for doc, score in search_results
        ]

        return SearchAndChatResponse(
            answer=answer,
            sources=sources,
            query=request.query,
        )
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
