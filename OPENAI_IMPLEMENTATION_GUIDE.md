# OpenAI 통합 구현 가이드

실제 코드 변경 사항을 포함한 단계별 구현 가이드입니다.

## 1단계: 의존성 추가

`app/requirements.txt`에 추가:
```
langchain-openai>=0.1.0
```

## 2단계: 환경 변수 설정

`.env` 파일 또는 Docker 환경 변수에 추가:
```bash
OPENAI_API_KEY=sk-your-api-key-here
```

## 3단계: 코드 변경

### 3.1 `app/app.py` 수정

```python
"""LangChain Hello World 앱 - pgvector 연동 예제."""

import os
import time
from typing import List

from langchain_core.documents import Document
# 변경: FakeEmbeddings 대신 OpenAIEmbeddings 사용
from langchain_openai import OpenAIEmbeddings
from langchain_postgres import PGVector


def get_vector_store():
    """벡터 스토어를 생성하고 반환합니다.

    Returns:
        PGVector 벡터 스토어 인스턴스.
    """
    db_host = os.getenv("POSTGRES_HOST", "postgres")
    db_port = os.getenv("POSTGRES_PORT", "5432")
    db_user = os.getenv("POSTGRES_USER", "langchain")
    db_password = os.getenv("POSTGRES_PASSWORD", "langchain")
    db_name = os.getenv("POSTGRES_DB", "langchain")

    connection_string = (
        f"postgresql://{db_user}:{db_password}@{db_host}:{db_port}/{db_name}"
    )

    # 변경: OpenAI Embeddings 사용
    embeddings = OpenAIEmbeddings(
        model="text-embedding-3-small",
        openai_api_key=os.getenv("OPENAI_API_KEY")
    )

    vector_store = PGVector(
        embeddings,
        connection=connection_string,
    )
    return vector_store
```

### 3.2 `rag_chain.py` 새로 생성

```python
"""RAG 체인 구성 모듈."""

from typing import List
from langchain_core.documents import Document
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.runnables import RunnablePassthrough
from langchain_openai import ChatOpenAI
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
```

### 3.3 `api_server.py` 확장

```python
"""FastAPI 서버 - LangChain RAG 시스템 API."""

import os
from typing import List, Optional

from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel

from .app import get_vector_store, test_pgvector, wait_for_postgres
from .rag_chain import create_rag_chain
from langchain_openai import ChatOpenAI

app = FastAPI(title="LangChain RAG API", version="1.0.0")

# CORS 설정
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# 요청/응답 모델
class SearchRequest(BaseModel):
    query: str
    k: int = 5

class ChatRequest(BaseModel):
    query: str

class DocumentResponse(BaseModel):
    content: str
    metadata: dict
    score: Optional[float] = None

class SearchResponse(BaseModel):
    results: List[DocumentResponse]
    query: str
    total: int

class ChatResponse(BaseModel):
    answer: str
    query: str
    model: str

# 전역 변수
_vector_store = None
_llm = None
_rag_chain = None

def get_vector_store_instance():
    """벡터 스토어 인스턴스를 가져옵니다."""
    global _vector_store
    if _vector_store is None:
        _vector_store = get_vector_store()
    return _vector_store

def get_llm():
    """LLM 인스턴스를 가져옵니다."""
    global _llm
    if _llm is None:
        api_key = os.getenv("OPENAI_API_KEY")
        if not api_key:
            raise ValueError("OPENAI_API_KEY 환경 변수가 설정되지 않았습니다.")
        _llm = ChatOpenAI(
            model="gpt-4o-mini",
            temperature=0.7,
            openai_api_key=api_key
        )
    return _llm

def get_rag_chain():
    """RAG 체인을 가져옵니다."""
    global _rag_chain
    if _rag_chain is None:
        vector_store = get_vector_store_instance()
        retriever = vector_store.as_retriever(search_kwargs={"k": 5})
        llm = get_llm()
        _rag_chain = create_rag_chain(llm, retriever)
    return _rag_chain

@app.on_event("startup")
async def startup_event():
    """서버 시작 시 초기화."""
    print("🚀 FastAPI 서버 시작 중...")

    db_host = os.getenv("POSTGRES_HOST", "postgres")
    db_port = os.getenv("POSTGRES_PORT", "5432")
    db_user = os.getenv("POSTGRES_USER", "langchain")
    db_password = os.getenv("POSTGRES_PASSWORD", "langchain")
    db_name = os.getenv("POSTGRES_DB", "langchain")

    connection_string = (
        f"postgresql://{db_user}:{db_password}@{db_host}:{db_port}/{db_name}"
    )

    wait_for_postgres(connection_string)
    test_pgvector(connection_string)
    get_vector_store_instance()
    print("✅ FastAPI 서버 준비 완료!")

@app.post("/chat", response_model=ChatResponse)
async def chat(request: ChatRequest):
    """RAG 기반 챗봇 응답을 생성합니다.

    Args:
        request: 챗봇 요청

    Returns:
        챗봇 응답
    """
    try:
        rag_chain = get_rag_chain()
        answer = rag_chain.invoke(request.query)

        return ChatResponse(
            answer=answer,
            query=request.query,
            model="gpt-4o-mini"
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/rag")
async def rag(request: ChatRequest):
    """검색 결과와 LLM 답변을 함께 반환합니다.

    Args:
        request: 챗봇 요청

    Returns:
        검색 결과와 LLM 답변
    """
    try:
        vector_store = get_vector_store_instance()

        # 1. 벡터 검색 수행
        search_results = vector_store.similarity_search_with_score(
            request.query, k=5
        )

        # 2. LLM 답변 생성
        rag_chain = get_rag_chain()
        answer = rag_chain.invoke(request.query)

        return {
            "answer": answer,
            "sources": [
                {
                    "content": doc.page_content,
                    "metadata": doc.metadata,
                    "score": float(score)
                }
                for doc, score in search_results
            ],
            "query": request.query
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

# 기존 엔드포인트들...
```

### 3.4 프론트엔드 수정 (`frontend/app/page.tsx`)

```typescript
// 기존 검색 대신 채팅 엔드포인트 사용
const handleSearch = async (searchQuery: string) => {
  // ... 기존 코드 ...

  try {
    // 옵션 1: 채팅만 사용
    const response = await fetch(
      `${process.env.NEXT_PUBLIC_API_URL || "http://localhost:8000"}/chat`,
      {
        method: "POST",
        headers: {
          "Content-Type": "application/json",
        },
        body: JSON.stringify({
          query: searchQuery,
        }),
      }
    );

    // 옵션 2: 검색 + 채팅 함께 사용
    // const response = await fetch(
    //   `${process.env.NEXT_PUBLIC_API_URL || "http://localhost:8000"}/rag`,
    //   ...
    // );

    const data = await response.json();

    // 응답 처리
    const assistantMessage: Message = {
      id: (Date.now() + 1).toString(),
      type: "assistant",
      content: data.answer, // LLM 답변
      timestamp: new Date(),
      sources: data.sources, // 검색 결과 (옵션)
    };
    setMessages((prev) => [...prev, assistantMessage]);
  } catch (err) {
    // 에러 처리
  }
};
```

## 4단계: Docker 환경 변수 추가

`docker-compose.yaml` 수정:
```yaml
langchain-app:
  # ... 기존 설정 ...
  environment:
    POSTGRES_HOST: postgres
    POSTGRES_PORT: 5432
    POSTGRES_USER: langchain
    POSTGRES_PASSWORD: langchain
    POSTGRES_DB: langchain
    OPENAI_API_KEY: ${OPENAI_API_KEY}  # 추가
```

`.env` 파일 생성 (프로젝트 루트):
```
OPENAI_API_KEY=sk-your-api-key-here
```

## 테스트

1. **Embeddings 테스트**:
```bash
curl -X POST http://localhost:8000/search \
  -H "Content-Type: application/json" \
  -d '{"query": "LangChain", "k": 3}'
```

2. **채팅 테스트**:
```bash
curl -X POST http://localhost:8000/chat \
  -H "Content-Type: application/json" \
  -d '{"query": "LangChain이 무엇인가요?"}'
```

3. **통합 테스트**:
```bash
curl -X POST http://localhost:8000/rag \
  -H "Content-Type: application/json" \
  -d '{"query": "LangChain이 무엇인가요?"}'
```

## 문제 해결

### API 키 오류
- 환경 변수가 제대로 설정되었는지 확인
- Docker 컨테이너 내부에서 환경 변수 확인: `docker exec langchain-app env | grep OPENAI`

### 임베딩 차원 불일치
- 기존 FakeEmbeddings(384차원)로 생성된 벡터는 재인덱싱 필요
- 또는 새로운 테이블 생성 후 마이그레이션

### 비용 관리
- OpenAI 대시보드에서 사용량 모니터링
- Rate limiting 구현
- 캐싱 전략 도입

