"""
chat_service.py 서빙 관련 서비스

단순 채팅/대화형 LLM 인터페이스

세션별 히스토리 관리, 요약, 토큰 절약 전략 등
"""

import torch
from transformers import AutoTokenizer, AutoModelForCausalLM, BitsAndBytesConfig
from peft import LoraConfig, get_peft_model, prepare_model_for_kbit_training

from ..models.midm_chat_model import load_midm_model


def get_chat_model(model_path: str = None):
    """채팅용 모델을 로드합니다.

    Args:
        model_path: 모델 경로. None이면 기본 경로 사용.

    Returns:
        (model, tokenizer) 튜플.
    """
    return load_midm_model(model_path=model_path)


def chat_with_model(model, tokenizer, query: str, **kwargs):
    """모델과 대화합니다.

    Args:
        model: 로드된 모델.
        tokenizer: 토크나이저.
        query: 사용자 질문.
        **kwargs: 생성 파라미터.

    Returns:
        생성된 답변.
    """
    messages = [{"role": "user", "content": query}]

    input_ids = tokenizer.apply_chat_template(
        messages,
        tokenize=True,
        add_generation_prompt=True,
        return_tensors="pt"
    )

    if torch.cuda.is_available():
        input_ids = input_ids.to("cuda")

    with torch.no_grad():
        outputs = model.generate(
            input_ids,
            max_new_tokens=kwargs.get("max_new_tokens", 128),
            do_sample=kwargs.get("do_sample", False),
            temperature=kwargs.get("temperature", 0.7),
            eos_token_id=tokenizer.eos_token_id,
        )

    response = tokenizer.decode(outputs[0][input_ids.shape[1]:], skip_special_tokens=True)
    return response


def train_with_qlora(model_path: str = None, training_data=None, output_dir: str = "./checkpoints"):
    """QLoRA 방식으로 모델을 학습합니다.

    Args:
        model_path: 모델 경로. None이면 기본 경로 사용.
        training_data: 학습 데이터.
        output_dir: 체크포인트 저장 경로.

    Returns:
        (학습된 모델, 토크나이저) 튜플.
    """
    # QLoRA 설정
    bnb_config = BitsAndBytesConfig(
        load_in_4bit=True,
        bnb_4bit_quant_type="nf4",
        bnb_4bit_compute_dtype=torch.bfloat16,
    )

    # 모델 경로 결정
    if model_path is None:
        from pathlib import Path
        current_dir = Path(__file__).parent.parent
        model_path = str(current_dir / "models" / "midm")

    # 모델을 4-bit로 로드
    model = AutoModelForCausalLM.from_pretrained(
        model_path,
        quantization_config=bnb_config,
        device_map="auto",
        trust_remote_code=True,
    )

    tokenizer = AutoTokenizer.from_pretrained(model_path, trust_remote_code=True)

    # LoRA 설정
    lora_config = LoraConfig(
        r=16,
        lora_alpha=32,
        target_modules=["q_proj", "k_proj", "v_proj", "o_proj"],
        lora_dropout=0.05,
        bias="none",
        task_type="CAUSAL_LM",
    )

    # 모델 준비
    model = prepare_model_for_kbit_training(model)
    model = get_peft_model(model, lora_config)

    # 학습 실행 (실제 학습 코드는 training_service에서 처리)
    return model, tokenizer
