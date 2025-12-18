"""RAG 체인 구성 모듈."""

from typing import List
from langchain_core.documents import Document
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.runnables import RunnablePassthrough
from langchain_core.output_parsers import StrOutputParser


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

