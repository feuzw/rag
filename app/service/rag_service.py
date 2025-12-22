"""
rag_service.py 서빙 관련 서비스

사용자의 질문을 받아 벡터 검색 + LLM 호출 + 응답 후처리까지 담당

rag_chain.py를 실제로 호출하는 "애플리케이션 서비스"
"""

from typing import List
from langchain_core.documents import Document
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.runnables import RunnablePassthrough
from langchain_core.output_parsers import StrOutputParser

# 환경에 따라 상대/절대 import 선택
try:
    from ..app import get_vector_store
    from ..models import get_llm
except ImportError:
    # 우분투 환경: 절대 import 사용
    from app import get_vector_store
    from models import get_llm

# 전역 변수
_vector_store = None
_rag_chain = None


def get_vector_store_instance():
    """벡터 스토어 인스턴스를 가져옵니다."""
    global _vector_store
    if _vector_store is None:
        _vector_store = get_vector_store()
    return _vector_store


def create_rag_chain(llm, retriever):
    """RAG 체인을 생성합니다.

    Args:
        llm: LangChain LLM 인스턴스
        retriever: 검색기 (Retriever)

    Returns:
        RAG 체인
    """
    # 프롬프트 템플릿
    prompt = ChatPromptTemplate.from_messages([
        ("system", """당신은 유용한 AI 어시스턴트입니다.
주어진 컨텍스트를 기반으로 사용자의 질문에 정확하고 도움이 되는 답변을 제공하세요.
컨텍스트에 없는 정보는 추측하지 말고, 모른다고 답변하세요.
답변의 마지막에 참고한 문서의 출처를 명시하세요.

컨텍스트:
{context}"""),
        ("human", "{question}")
    ])

    # 체인 구성
    chain = (
        {
            "context": retriever,
            "question": RunnablePassthrough()
        }
        | prompt
        | llm
        | StrOutputParser()
    )

    return chain


def get_rag_chain():
    """RAG 체인을 가져옵니다."""
    global _rag_chain
    if _rag_chain is None:
        vector_store = get_vector_store_instance()
        retriever = vector_store.as_retriever(search_kwargs={"k": 5})
        llm = get_llm()
        _rag_chain = create_rag_chain(llm, retriever)
    return _rag_chain


def invoke_rag(query: str) -> str:
    """RAG 체인을 실행하여 답변을 생성합니다.

    Args:
        query: 사용자 질문.

    Returns:
        생성된 답변.
    """
    rag_chain = get_rag_chain()
    return rag_chain.invoke(query)


def search_with_rag(query: str, k: int = 5) -> tuple[str, List[tuple[Document, float]]]:
    """벡터 검색과 RAG 답변을 함께 반환합니다.

    Args:
        query: 사용자 질문.
        k: 검색할 문서 수.

    Returns:
        (답변, 검색 결과 리스트) 튜플.
    """
    vector_store = get_vector_store_instance()
    search_results = vector_store.similarity_search_with_score(query, k=k)

    try:
        answer = invoke_rag(query)
    except ValueError:
        answer = "LLM 서비스를 사용할 수 없어 검색 결과만 제공합니다."

    return answer, search_results
