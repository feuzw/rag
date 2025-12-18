# OpenAI 통합 전략

현재 RAG 시스템에 OpenAI를 연결하는 전략 가이드입니다.

## 현재 시스템 구조

- **Embeddings**: `FakeEmbeddings` (더미 임베딩)
- **Vector Store**: `PGVector` (pgvector)
- **API**: FastAPI 기반 검색 API
- **기능**: 벡터 유사도 검색만 수행 (답변 생성 없음)

## 통합 전략

### 1단계: OpenAI Embeddings 통합

**목표**: FakeEmbeddings를 OpenAI Embeddings로 교체

#### 필요한 패키지
```bash
langchain-openai>=0.1.0
```

#### 변경 사항

**`app.py` 수정**:
```python
# 기존
from langchain_core.embeddings import FakeEmbeddings
embeddings = FakeEmbeddings(size=384)

# 변경 후
from langchain_openai import OpenAIEmbeddings
embeddings = OpenAIEmbeddings(
    model="text-embedding-3-small",  # 또는 text-embedding-3-large
    openai_api_key=os.getenv("OPENAI_API_KEY")
)
```

**환경 변수 추가**:
```bash
OPENAI_API_KEY=your-api-key-here
```

**주의사항**:
- 기존 FakeEmbeddings로 생성된 벡터는 재인덱싱 필요
- OpenAI Embeddings는 1536차원 (text-embedding-3-small) 또는 3072차원 (text-embedding-3-large)

### 2단계: OpenAI LLM 통합 (RAG 체인 구성)

**목표**: 검색된 문서를 기반으로 LLM이 답변 생성

#### 필요한 패키지
```bash
langchain-openai>=0.1.0
```

#### RAG 체인 구성

**새 파일 생성: `rag_chain.py`**
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


def format_docs(docs: List[Document]) -> str:
    """문서 리스트를 문자열로 포맷팅합니다.

    Args:
        docs: 문서 리스트

    Returns:
        포맷팅된 문자열
    """
    return "\n\n".join([
        f"문서 {i+1}:\n{doc.page_content}\n[출처: {doc.metadata.get('source', 'unknown')}]"
        for i, doc in enumerate(docs)
    ])
```

### 3단계: API 엔드포인트 확장

**`app/api_server.py`에 새로운 엔드포인트 추가**:

```python
from langchain_openai import ChatOpenAI, OpenAIEmbeddings
from .rag_chain import create_rag_chain

# 전역 LLM 및 RAG 체인
_llm = None
_rag_chain = None

def get_llm():
    """LLM 인스턴스를 가져옵니다."""
    global _llm
    if _llm is None:
        _llm = ChatOpenAI(
            model="gpt-4o-mini",  # 또는 gpt-4o, gpt-3.5-turbo
            temperature=0.7,
            openai_api_key=os.getenv("OPENAI_API_KEY")
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

@app.post("/chat")
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

        return {
            "answer": answer,
            "query": request.query,
            "model": "gpt-4o-mini"
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
```

### 4단계: 하이브리드 접근 방식 (권장)

**검색 + 생성 통합 엔드포인트**:

```python
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
```

## 구현 단계별 체크리스트

### Phase 1: Embeddings 교체
- [ ] `app/requirements.txt`에 `langchain-openai` 추가
- [ ] 환경 변수에 `OPENAI_API_KEY` 설정
- [ ] `app/app.py`에서 `FakeEmbeddings` → `OpenAIEmbeddings` 교체
- [ ] 기존 벡터 데이터 재인덱싱 (선택사항)
- [ ] 테스트: 검색 기능이 정상 작동하는지 확인

### Phase 2: LLM 통합
- [ ] `app/rag_chain.py` 파일 생성
- [ ] `app/api_server.py`에 LLM 초기화 코드 추가
- [ ] `/chat` 엔드포인트 추가
- [ ] 프론트엔드에서 `/chat` 엔드포인트 호출하도록 수정
- [ ] 테스트: LLM 답변이 생성되는지 확인

### Phase 3: 최적화
- [ ] 프롬프트 튜닝
- [ ] 검색 결과 개수 조정 (k 값)
- [ ] 응답 스트리밍 구현 (선택사항)
- [ ] 에러 핸들링 강화
- [ ] 비용 모니터링

## 비용 고려사항

### Embeddings 비용
- `text-embedding-3-small`: $0.02 / 1M tokens
- `text-embedding-3-large`: $0.13 / 1M tokens

### LLM 비용
- `gpt-4o-mini`: $0.15 / 1M input tokens, $0.60 / 1M output tokens
- `gpt-4o`: $2.50 / 1M input tokens, $10.00 / 1M output tokens
- `gpt-3.5-turbo`: $0.50 / 1M input tokens, $1.50 / 1M output tokens

### 최적화 팁
1. **캐싱**: 동일한 쿼리에 대한 임베딩 캐싱
2. **배치 처리**: 여러 문서를 한 번에 임베딩
3. **모델 선택**: 용도에 맞는 모델 선택 (작은 모델로 시작)
4. **토큰 제한**: 프롬프트와 컨텍스트 길이 최적화

## 보안 고려사항

1. **API 키 관리**
   - 환경 변수 사용 (절대 코드에 하드코딩 금지)
   - Docker secrets 또는 Kubernetes secrets 사용
   - `.env` 파일은 `.gitignore`에 추가

2. **Rate Limiting**
   - OpenAI API 호출 제한 설정
   - 사용자별 요청 제한 구현

3. **데이터 프라이버시**
   - 민감한 데이터는 OpenAI로 전송하지 않기
   - 필요시 데이터 마스킹 또는 필터링

## 모니터링 및 로깅

```python
import logging

logger = logging.getLogger(__name__)

@app.post("/chat")
async def chat(request: ChatRequest):
    logger.info(f"Chat request: {request.query}")
    start_time = time.time()

    try:
        answer = rag_chain.invoke(request.query)
        elapsed = time.time() - start_time
        logger.info(f"Chat response generated in {elapsed:.2f}s")
        return {"answer": answer}
    except Exception as e:
        logger.error(f"Chat error: {str(e)}")
        raise
```

## 다음 단계

1. **스트리밍 응답**: 실시간으로 답변 생성
2. **멀티 턴 대화**: 대화 히스토리 관리
3. **소스 인용**: 답변에 출처 표시
4. **사용자 피드백**: 답변 품질 평가 시스템

