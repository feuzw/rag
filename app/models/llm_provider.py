"""LLM 프로바이더 및 주입 관리 모듈."""

from typing import Optional
from langchain_core.language_models import BaseChatModel


class LLMProvider:
    """LLM 프로바이더 추상화 클래스.

    다양한 LLM 모델을 주입하기 위한 인터페이스를 제공합니다.
    """

    def __init__(self, llm: Optional[BaseChatModel] = None) -> None:
        """LLM 프로바이더를 초기화합니다.

        Args:
            llm: 주입할 LLM 모델 인스턴스. None인 경우 지연 초기화됩니다.
        """
        self._llm: Optional[BaseChatModel] = llm

    def get_llm(self) -> BaseChatModel:
        """LLM 인스턴스를 반환합니다.

        Returns:
            LLM 인스턴스.

        Raises:
            ValueError: LLM이 설정되지 않았고 초기화할 수 없는 경우.
        """
        if self._llm is None:
            raise ValueError(
                "LLM이 설정되지 않았습니다. set_llm() 메서드를 사용하여 LLM을 주입하세요."
            )
        return self._llm

    def set_llm(self, llm: BaseChatModel) -> None:
        """LLM 인스턴스를 주입합니다.

        Args:
            llm: 주입할 LLM 모델 인스턴스.
        """
        self._llm = llm


# 전역 LLM 프로바이더 인스턴스
_llm_provider: Optional[LLMProvider] = None


def get_llm_provider() -> LLMProvider:
    """전역 LLM 프로바이더 인스턴스를 가져옵니다.

    Returns:
        LLM 프로바이더 인스턴스.
    """
    global _llm_provider
    if _llm_provider is None:
        _llm_provider = LLMProvider()
    return _llm_provider


def set_llm_provider(provider: LLMProvider) -> None:
    """전역 LLM 프로바이더 인스턴스를 설정합니다.

    Args:
        provider: 설정할 LLM 프로바이더 인스턴스.
    """
    global _llm_provider
    _llm_provider = provider


def get_llm() -> BaseChatModel:
    """전역 LLM 인스턴스를 가져옵니다.

    Returns:
        LLM 인스턴스.

    Raises:
        ValueError: LLM이 설정되지 않은 경우.
    """
    provider = get_llm_provider()
    return provider.get_llm()

