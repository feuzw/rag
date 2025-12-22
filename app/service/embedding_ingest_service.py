"""
embedding_ingest_service.py 학습 관련 서비스

문서를 받아 :
임베딩 생성 +
벡터스토어 업서트까지 한번에 처리

배치/주기적인 인덱싱 작업도 이 서비스 레벨에서 처리
"""

from langchain_core.documents import Document

# 환경에 따라 상대/절대 import 선택
try:
    from ..app import get_vector_store
except ImportError:
    # 우분투 환경: 절대 import 사용
    from app import get_vector_store

# 전역 변수
_vector_store = None


def get_vector_store_instance():
    """벡터 스토어 인스턴스를 가져옵니다."""
    global _vector_store
    if _vector_store is None:
        _vector_store = get_vector_store()
    return _vector_store


def add_document(content: str, metadata: dict = None):
    """단일 문서를 벡터 스토어에 추가합니다.

    Args:
        content: 문서 내용.
        metadata: 문서 메타데이터.

    Returns:
        추가 결과.
    """
    vector_store = get_vector_store_instance()
    doc = Document(
        page_content=content,
        metadata=metadata or {},
    )
    vector_store.add_documents([doc])
    return {"message": "문서가 성공적으로 추가되었습니다.", "status": "success"}


def add_documents(documents: list[dict]):
    """여러 문서를 벡터 스토어에 추가합니다.

    Args:
        documents: 문서 리스트 (각 문서는 content와 metadata를 포함).

    Returns:
        추가 결과.
    """
    vector_store = get_vector_store_instance()
    docs = [
        Document(
            page_content=doc["content"],
            metadata=doc.get("metadata", {}),
        )
        for doc in documents
    ]
    vector_store.add_documents(docs)
    return {
        "message": f"{len(docs)}개의 문서가 성공적으로 추가되었습니다.",
        "status": "success",
        "count": len(docs),
    }
