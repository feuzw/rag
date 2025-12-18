"""Mi:dm 모델을 위한 LangChain ChatModel 래퍼 및 로더."""

from __future__ import annotations

from pathlib import Path
from typing import TYPE_CHECKING, Any, Optional

from langchain_core.language_models import BaseChatModel
from langchain_core.messages import AIMessage, BaseMessage
from langchain_core.messages.ai import UsageMetadata
from langchain_core.outputs import ChatGeneration, ChatResult
from pydantic import Field, PrivateAttr
from typing_extensions import override

if TYPE_CHECKING:
    from langchain_core.callbacks import CallbackManagerForLLMRun

    from transformers import AutoModelForCausalLM, AutoTokenizer


def load_midm_model(
    model_path: Optional[str] = None,
    torch_dtype: str = "auto",
    device_map: str = "auto",
    trust_remote_code: bool = True,
) -> tuple["AutoModelForCausalLM", "AutoTokenizer"]:
    """Mi:dm 모델과 토크나이저를 로드합니다.

    Args:
        model_path: 로컬 모델 경로. None인 경우 기본 경로 (app/models/midm/) 사용.
        torch_dtype: PyTorch 데이터 타입. "auto", "float16", "float32", "bfloat16" 등.
        device_map: 디바이스 매핑. "auto", "cpu", "cuda:0" 등.
        trust_remote_code: 원격 코드 실행 허용 여부. Mi:dm 모델은 필수입니다.

    Returns:
        (모델, 토크나이저) 튜플.

    Raises:
        ImportError: transformers 또는 torch가 설치되지 않은 경우.
        Exception: 모델 로딩 중 오류가 발생한 경우.
    """
    try:
        from transformers import AutoModelForCausalLM, AutoTokenizer
        import torch

        # 모델 경로 결정 (기본값: app/models/midm/)
        if model_path is None:
            # 현재 파일의 디렉토리 기준으로 midm 폴더 경로 계산
            current_dir = Path(__file__).parent
            model_path = str(current_dir / "midm")

        # torch_dtype 변환
        if torch_dtype == "auto":
            dtype = torch_dtype
        elif torch_dtype == "float16":
            dtype = torch.float16
        elif torch_dtype == "float32":
            dtype = torch.float32
        elif torch_dtype == "bfloat16":
            dtype = torch.bfloat16
        else:
            dtype = torch_dtype

        # 모델 로드
        model = AutoModelForCausalLM.from_pretrained(
            model_path,
            torch_dtype=dtype,
            device_map=device_map,
            trust_remote_code=trust_remote_code,
        )

        # 토크나이저 로드
        tokenizer = AutoTokenizer.from_pretrained(
            model_path,
            trust_remote_code=trust_remote_code,
        )

        return model, tokenizer

    except ImportError as e:
        raise ImportError(
            "transformers 또는 torch가 설치되지 않았습니다. "
            "다음 명령어로 설치하세요: pip install transformers torch"
        ) from e
    except Exception as e:
        raise Exception(f"Mi:dm 모델 로딩 실패: {str(e)}") from e


class ChatMidm(BaseChatModel):
    """Mi:dm 모델을 위한 LangChain ChatModel.

    Mi:dm 모델을 LangChain과 통합하여 사용할 수 있도록 하는 래퍼 클래스입니다.

    Example:
        ```python
        from app.models.midm_chat_model import ChatMidm
        from langchain_core.messages import HumanMessage

        # 모델 초기화
        model = ChatMidm(
            temperature=0.7,
            max_tokens=512,
        )

        # 메시지 전송
        messages = [HumanMessage(content="안녕하세요!")]
        response = model.invoke(messages)
        print(response.content)
        ```
    """

    model_path: Optional[str] = Field(
        default=None,
        description="로컬 모델 경로. None인 경우 기본 경로 (app/models/midm/) 사용",
    )
    """로컬 모델 경로. None인 경우 app/models/midm/ 사용."""
    temperature: float = Field(default=0.7, description="생성 온도")
    """생성 온도 (0.0 ~ 1.0)."""
    max_tokens: int = Field(default=512, description="최대 토큰 수")
    """최대 생성 토큰 수."""
    top_p: float = Field(default=0.9, description="Nucleus sampling의 top_p")
    """Nucleus sampling의 top_p 값."""
    top_k: int = Field(default=50, description="Top-k sampling의 k")
    """Top-k sampling의 k 값."""
    do_sample: bool = Field(default=True, description="샘플링 사용 여부")
    """샘플링 사용 여부."""
    torch_dtype: str = Field(default="auto", description="PyTorch 데이터 타입")
    """PyTorch 데이터 타입."""
    device_map: str = Field(default="auto", description="디바이스 매핑")
    """디바이스 매핑."""
    trust_remote_code: bool = Field(default=True, description="원격 코드 신뢰 여부")
    """원격 코드 신뢰 여부. Mi:dm 모델은 필수입니다."""

    # 내부 모델과 토크나이저 (런타임에 로드됨) - PrivateAttr 사용
    _model: Optional["AutoModelForCausalLM"] = PrivateAttr(default=None)
    _tokenizer: Optional["AutoTokenizer"] = PrivateAttr(default=None)

    def __init__(self, **kwargs: Any) -> None:
        """ChatMidm 인스턴스를 초기화합니다.

        Args:
            **kwargs: ChatMidm 필드 값들.
        """
        super().__init__(**kwargs)
        # 모델은 지연 로딩됩니다 (첫 호출 시 로드)

    def _load_model(self) -> None:
        """모델과 토크나이저를 로드합니다."""
        if self._model is None or self._tokenizer is None:
            self._model, self._tokenizer = load_midm_model(
                model_path=self.model_path,
                torch_dtype=self.torch_dtype,
                device_map=self.device_map,
                trust_remote_code=self.trust_remote_code,
            )

    @override
    def _generate(
        self,
        messages: list[BaseMessage],
        stop: Optional[list[str]] = None,
        run_manager: Optional["CallbackManagerForLLMRun"] = None,
        **kwargs: Any,
    ) -> ChatResult:
        """메시지로부터 응답을 생성합니다.

        Args:
            messages: 입력 메시지 리스트.
            stop: 생성 중단 문자열 리스트.
            run_manager: 콜백 매니저.
            **kwargs: 추가 키워드 인자.

        Returns:
            ChatResult 객체.
        """
        # 모델 로드 (지연 로딩)
        self._load_model()

        # 메시지를 텍스트 프롬프트로 변환
        prompt = self._format_messages_to_prompt(messages)

        # 토크나이징
        inputs = self._tokenizer.encode(prompt, return_tensors="pt")
        input_ids = inputs.to(self._model.device)

        # 생성 파라미터
        generation_kwargs = {
            "temperature": kwargs.get("temperature", self.temperature),
            "max_new_tokens": kwargs.get("max_tokens", self.max_tokens),
            "top_p": kwargs.get("top_p", self.top_p),
            "top_k": kwargs.get("top_k", self.top_k),
            "do_sample": kwargs.get("do_sample", self.do_sample),
        }

        # 생성
        outputs = self._model.generate(
            input_ids,
            **generation_kwargs,
        )

        # 디코딩
        generated_text = self._tokenizer.decode(
            outputs[0][input_ids.shape[1]:],
            skip_special_tokens=True
        )

        # Stop 문자열로 자르기
        if stop:
            for stop_str in stop:
                if stop_str in generated_text:
                    generated_text = generated_text.split(stop_str)[0]

        # 토큰 수 계산 (근사치)
        input_token_count = input_ids.shape[1]
        output_token_count = outputs[0].shape[0] - input_ids.shape[1]

        # AIMessage 생성
        message = AIMessage(
            content=generated_text.strip(),
            response_metadata={
                "model": "Midm-2.0-Mini-Instruct",
                "temperature": generation_kwargs["temperature"],
            },
            usage_metadata=UsageMetadata(
                input_tokens=input_token_count,
                output_tokens=output_token_count,
                total_tokens=input_token_count + output_token_count,
            ),
        )

        generation = ChatGeneration(message=message)
        return ChatResult(generations=[generation])

    def _format_messages_to_prompt(self, messages: list[BaseMessage]) -> str:
        """LangChain 메시지를 Mi:dm 프롬프트 형식으로 변환합니다.

        Args:
            messages: LangChain 메시지 리스트.

        Returns:
            변환된 프롬프트 문자열.
        """
        # 토크나이저의 chat template 사용 시도
        if (
            self._tokenizer is not None
            and hasattr(self._tokenizer, "apply_chat_template")
            and self._tokenizer.chat_template is not None
        ):
            # LangChain 메시지를 dict 형식으로 변환
            formatted_messages = []
            for msg in messages:
                if msg.type == "system":
                    formatted_messages.append({"role": "system", "content": str(msg.content)})
                elif msg.type == "human" or msg.type == "user":
                    formatted_messages.append({"role": "user", "content": str(msg.content)})
                elif msg.type == "ai" or msg.type == "assistant":
                    formatted_messages.append({"role": "assistant", "content": str(msg.content)})
                else:
                    # 기타 메시지 타입은 user로 처리
                    formatted_messages.append({"role": "user", "content": str(msg.content)})

            try:
                prompt = self._tokenizer.apply_chat_template(
                    formatted_messages,
                    tokenize=False,
                    add_generation_prompt=True,
                )
                return prompt
            except Exception:
                # chat template 적용 실패 시 기본 형식 사용
                pass

        # 기본 형식: 마지막 메시지만 사용
        if messages:
            return str(messages[-1].content)
        return ""

    @property
    @override
    def _llm_type(self) -> str:
        """모델 타입을 반환합니다."""
        return "midm-chat-model"

    @property
    @override
    def _identifying_params(self) -> dict[str, Any]:
        """모델 식별 파라미터를 반환합니다."""
        return {
            "model_path": self.model_path,
            "temperature": self.temperature,
            "max_tokens": self.max_tokens,
            "top_p": self.top_p,
            "top_k": self.top_k,
            "do_sample": self.do_sample,
        }

