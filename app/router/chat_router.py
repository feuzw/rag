"""
FastAPI 기준의 API 엔드포인트 계층

chat_router.py
POST /api/chat
세션 ID, 메시지 리스트 등을 받아 대화형 응답 반환
"""

from fastapi import APIRouter, HTTPException
from pydantic import BaseModel

# 환경에 따라 상대/절대 import 선택
try:
    from ..service.chat_service import get_chat_model, chat_with_model
except ImportError:
    # 우분투 환경: 절대 import 사용
    from service.chat_service import get_chat_model, chat_with_model

router = APIRouter(tags=["chat"])

# 전역 변수
_chat_model = None
_chat_tokenizer = None


class ChatRequest(BaseModel):
    """채팅 요청 모델."""

    query: str


class ChatResponse(BaseModel):
    """채팅 응답 모델."""

    answer: str
    query: str
    model: str


def get_chat_model_instance():
    """채팅 모델 인스턴스를 가져옵니다."""
    global _chat_model, _chat_tokenizer
    if _chat_model is None or _chat_tokenizer is None:
        _chat_model, _chat_tokenizer = get_chat_model()
    return _chat_model, _chat_tokenizer


@router.post("/chat", response_model=ChatResponse)
async def chat(request: ChatRequest):
    """채팅 응답을 생성합니다.

    Args:
        request: 챗봇 요청.

    Returns:
        챗봇 응답.
    """
    try:
        model, tokenizer = get_chat_model_instance()
        answer = chat_with_model(model, tokenizer, request.query)

        return ChatResponse(
            answer=answer,
            query=request.query,
            model="midm-chat",
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
