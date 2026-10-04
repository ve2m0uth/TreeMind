import openai
from abc import abstractmethod
import base64
import time


class ModelRequestError(RuntimeError):
    """Raised after a model request has exhausted its bounded retries."""


class BaseModel:
    def __init__(self):
        pass

    @abstractmethod
    def get_model_response(self, message):
        pass

class OpenAIModel(BaseModel):
    def __init__(self, base_url: str, api_key: str, model: str, temperature: float,
                 max_retries: int = 2, retry_base_seconds: float = 1.0):
        super().__init__()
        self.base_url = base_url
        self.api_key = api_key
        self.model = model
        self.temperature = temperature
        self.max_retries = max(0, int(max_retries))
        self.retry_base_seconds = max(0.0, float(retry_base_seconds))
        self.client = openai.OpenAI(
            base_url=self.base_url,
            api_key=self.api_key,
            max_retries=0,
        )

    def get_model_response(self, message):
        last_error = None

        for attempt in range(self.max_retries + 1):
            try:
                response = self.client.chat.completions.create(
                    model=self.model,
                    messages=message,
                    n=1,
                    stop=None,
                    temperature=self.temperature,
                )
                return response.choices[0].message.content or ""
            except Exception as exc:
                last_error = exc
                if attempt < self.max_retries:
                    time.sleep(self.retry_base_seconds * (2 ** attempt))

        raise ModelRequestError(
            f"Model request failed after {self.max_retries + 1} attempts: {last_error}"
        ) from last_error


class QwenModel(BaseModel):
    """Qwen model accessed through Alibaba Cloud's OpenAI-compatible API."""

    def __init__(self, base_url: str, api_key: str, model: str, temperature: float,
                 max_retries: int = 2, retry_base_seconds: float = 1.0):
        super().__init__()
        self.base_url = base_url
        self.api_key = api_key
        self.model = model
        self.temperature = temperature
        self.max_retries = max(0, int(max_retries))
        self.retry_base_seconds = max(0.0, float(retry_base_seconds))
        self.client = openai.OpenAI(
            base_url=self.base_url,
            api_key=self.api_key,
            max_retries=0,
        )

    def get_model_response(self, message):
        last_error = None

        for attempt in range(self.max_retries + 1):
            try:
                response = self.client.chat.completions.create(
                    model=self.model,
                    messages=message,
                    n=1,
                    stop=None,
                    temperature=self.temperature,
                )
                return response.choices[0].message.content or ""
            except Exception as exc:
                last_error = exc
                if attempt < self.max_retries:
                    time.sleep(self.retry_base_seconds * (2 ** attempt))

        raise ModelRequestError(
            f"Qwen model request failed after "
            f"{self.max_retries + 1} attempts: {last_error}"
        ) from last_error


def load_llm(configs):
    provider = str(configs.get("MODEL", "")).strip().lower()
    if provider == "openai":
        mllm = OpenAIModel(base_url=configs["OPENAI_API_BASE"],
                           api_key=configs["OPENAI_API_KEY"],
                           model=configs["OPENAI_API_MODEL"],
                           temperature=configs["TEMPERATURE"],
                           max_retries=configs.get("MODEL_MAX_RETRIES", 2),
                           retry_base_seconds=configs.get("MODEL_RETRY_BASE_SECONDS", 1.0),
                           )
    elif provider == "qwen":
        api_key = configs.get("QWEN_API_KEY") or configs.get("DASHSCOPE_API_KEY")
        if not api_key:
            raise ValueError(
                "Qwen API key is missing. Set QWEN_API_KEY in config.yaml "
                "or DASHSCOPE_API_KEY in the environment."
            )
        mllm = QwenModel(
            base_url=configs.get("QWEN_API_BASE")
            or "https://dashscope.aliyuncs.com/compatible-mode/v1",
            api_key=api_key,
            model=configs.get("QWEN_API_MODEL") or "qwen3-vl-plus",
            temperature=configs["TEMPERATURE"],
            max_retries=configs.get("MODEL_MAX_RETRIES", 2),
            retry_base_seconds=configs.get("MODEL_RETRY_BASE_SECONDS", 1.0),
        )
    else:
        raise ValueError(f"Unsupported model provider: {configs.get('MODEL')}")
    return mllm


def encode_image(image_path):
    with open(image_path, "rb") as image_file:
        return base64.b64encode(image_file.read()).decode('utf-8')
