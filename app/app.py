"""LangChain Hello World 앱 - pgvector 연동 예제."""

import os
import time
from typing import List
from urllib.parse import urlparse

from langchain_core.documents import Document
from langchain_openai import OpenAIEmbeddings
from langchain_postgres import PGVector


def wait_for_postgres(connection_string: str, max_retries: int = 30) -> None:
    """PostgreSQL 연결을 기다립니다.

    Args:
        connection_string: PostgreSQL 연결 문자열.
        max_retries: 최대 재시도 횟수.

    Raises:
        Exception: 최대 재시도 횟수를 초과한 경우.
    """
    import psycopg2

    for i in range(max_retries):
        try:
            conn = psycopg2.connect(connection_string)
            conn.close()
            print("✅ PostgreSQL 연결 성공!")
            return
        except Exception as e:
            if i == 0:
                print(f"⏳ PostgreSQL 연결 대기 중... ({e})")
            time.sleep(2)
    raise Exception("PostgreSQL 연결 실패: 최대 재시도 횟수 초과")


def get_vector_store():
    """벡터 스토어를 생성하고 반환합니다.

    Returns:
        PGVector 벡터 스토어 인스턴스.
    """
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

    # OpenAI Embeddings 사용
    api_key = os.getenv("OPENAI_API_KEY")
    if not api_key:
        raise ValueError(
            "OPENAI_API_KEY 환경 변수가 설정되지 않았습니다. "
            "환경 변수를 설정하거나 .env 파일에 추가하세요."
        )

    embeddings = OpenAIEmbeddings(
        model="text-embedding-3-small",
        openai_api_key=api_key,
    )

    vector_store = PGVector(
        embeddings,
        connection=connection_string,
    )
    return vector_store


def test_pgvector(connection_string: str) -> None:
    """pgvector 확장이 설치되어 있는지 간단히 테스트하고, 없으면 생성합니다.

    Args:
        connection_string: PostgreSQL 연결 문자열.
    """
    import psycopg2

    conn = psycopg2.connect(connection_string)
    conn.autocommit = True
    cursor = conn.cursor()

    # pgvector 확장이 있는지 확인
    cursor.execute("SELECT EXISTS(SELECT 1 FROM pg_extension WHERE extname = 'vector');")
    has_extension = cursor.fetchone()[0]

    if not has_extension:
        print("📦 pgvector 확장이 없습니다. 설치 중...")
        try:
            cursor.execute("CREATE EXTENSION IF NOT EXISTS vector;")
            print("✅ pgvector 확장 설치 완료!")
        except Exception as e:
            cursor.close()
            conn.close()
            raise Exception(f"❌ pgvector 확장 설치 실패: {e}")

    # 버전 확인
    cursor.execute("SELECT extversion FROM pg_extension WHERE extname = 'vector';")
    version = cursor.fetchone()[0]
    print(f"✅ pgvector 확장 확인 (버전: {version})")

    cursor.close()
    conn.close()


def main() -> None:
    """LangChain Hello World 앱의 메인 함수.

    pgvector와 연동하여 벡터 스토어를 생성하고,
    문서를 추가한 후 유사도 검색을 수행합니다.
    """
    print("🚀 LangChain Hello World 앱 시작!")

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
        print(f"📊 PostgreSQL 연결 정보: {db_host}:{db_port}/{db_name}")
    else:
        # 연결 문자열에서 호스트와 데이터베이스명 추출 (표시용)
        parsed = urlparse(connection_string)
        print(f"📊 PostgreSQL 연결 정보: {parsed.hostname}:{parsed.port or 5432}/{parsed.path[1:]}")

    # PostgreSQL 연결 대기
    wait_for_postgres(connection_string)

    # pgvector 확장 테스트
    print("🔍 pgvector 확장 확인 중...")
    test_pgvector(connection_string)

    # OpenAI Embeddings 사용
    api_key = os.getenv("OPENAI_API_KEY")
    if not api_key:
        raise ValueError("OPENAI_API_KEY 환경 변수가 설정되지 않았습니다.")

    embeddings = OpenAIEmbeddings(
        model="text-embedding-3-small",
        openai_api_key=api_key,
    )

    print("📝 벡터 스토어 생성 중...")

    # PGVector 벡터 스토어 생성
    # embeddings는 첫 번째 위치 인자(필수), connection은 키워드 인자
    vector_store = PGVector(
        embeddings,
        connection=connection_string,
    )

    print("✅ 벡터 스토어 생성 완료!")

    # 샘플 문서 생성
    documents = [
        Document(
            page_content="LangChain은 LLM 기반 애플리케이션을 구축하기 위한 프레임워크입니다.",
            metadata={"source": "intro", "type": "framework"},
        ),
        Document(
            page_content="pgvector는 PostgreSQL에서 벡터 유사도 검색을 가능하게 하는 확장입니다.",
            metadata={"source": "pgvector", "type": "database"},
        ),
        Document(
            page_content="Hello World는 프로그래밍에서 가장 기본적인 예제 프로그램입니다.",
            metadata={"source": "hello", "type": "example"},
        ),
    ]

    print("📚 문서 추가 중...")
    vector_store.add_documents(documents)
    print("✅ 문서 추가 완료!")

    # 유사도 검색 테스트
    print("\n🔍 유사도 검색 테스트:")
    query = "프레임워크"
    results: List[Document] = vector_store.similarity_search(query, k=2)

    print(f"\n검색 쿼리: '{query}'")
    print(f"검색 결과 ({len(results)}개):\n")
    for i, doc in enumerate(results, 1):
        print(f"{i}. {doc.page_content}")
        print(f"   메타데이터: {doc.metadata}\n")

    # 점수와 함께 검색
    print("📊 점수와 함께 검색:")
    results_with_score = vector_store.similarity_search_with_score(query, k=2)

    for i, (doc, score) in enumerate(results_with_score, 1):
        print(f"{i}. [유사도: {score:.4f}] {doc.page_content}")
        print(f"   메타데이터: {doc.metadata}\n")

    print("🎉 LangChain Hello World 앱 실행 완료!")


if __name__ == "__main__":
    main()

