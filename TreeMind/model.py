import openai
from abc import abstractmethod
from http import HTTPStatus
import dashscope
import base64


class BaseModel:
    def __init__(self):
        pass

    @abstractmethod
    def get_model_response(self, message):
        pass


class OpenAIModel(BaseModel):
    def __init__(self, base_url: str, api_key: str, model: str, temperature: float):
        super().__init__()
        self.base_url = base_url
        self.api_key = api_key
        self.model = model
        self.temperature = temperature
        self.client = openai.OpenAI(
            base_url=self.base_url,
            api_key=self.api_key,
        )

    def get_model_response(self, message):
        try:
            response = self.client.chat.completions.create(
                model=self.model,
                messages = message,
                n=1,
                stop=None,
                temperature=self.temperature,
            )
            return response.choices[0].message.content
        except Exception as e:
            print(str(e))
            exit(0)


def load_llm(configs):
    if configs["MODEL"] == "OpenAI":
        mllm = OpenAIModel(base_url=configs["OPENAI_API_BASE"],
                           api_key=configs["OPENAI_API_KEY"],
                           model=configs["OPENAI_API_MODEL"],
                           temperature=configs["TEMPERATURE"],
                           )
    else:
        print("No such model!")
        exit(0)
    return mllm


def encode_image(image_path):
    with open(image_path, "rb") as image_file:
        return base64.b64encode(image_file.read()).decode('utf-8')