from .llm_provider_model import LLmOutput, LlmError
from google import genai
from utils import current_milli_time


class GeminiProvider:
    """
    LLM Gemini
    """

    def __init__(self, api_keys: list[str],
                 model_name: str = "gemini-3.8-flash",
                 url: str = "https://generativelanguage.googleapis.com"
                 ) -> None:
        """
        Gemini Argument Initialization

        Args:
            api_keys (list[str]): the usable API keys
            model_name (str) = The model name
            url (str) = The URL to use the model
        """
        self.url: str = url
        self.model_name: str = model_name
        self.api_keys: list[str] = api_keys

        self.curr_id: int = 0
        self.max_id: int = len(api_keys)

        self.client = genai.Client(api_key=self.api_keys[self.curr_id])

    def use_next_key(self) -> bool:
        """
        Move to the next API key, generate the corresponding model
        """
        if self.curr_id == self.max_id - 1:
            return False

        self.curr_id += 1
        self.client = genai.Client(api_key=self.api_keys[self.curr_id])
        return True

    def generate(self, prompt: str) -> LLmOutput:
        """
        Method for generating model output based on a request

        Argument:
            prompt(str): The request

        Return:
            (LLmOutput): The AI ​​output
        """
        start_time: float = current_milli_time()

        try:
            content = self.client.interactions.create(
                model=self.model_name,
                input=prompt
            )
        except Exception as e:
            if self.use_next_key():
                return self.generate(prompt)
            raise LlmError(e)

        return LLmOutput(
            content=content.output_text,
            reponse_time=start_time - current_milli_time(),
            total_input_tokens=content.usage.total_input_tokens,
            total_output_tokens=content.usage.total_output_tokens,
            api_url=self.url,
            model_name=self.model_name
        )


"""
Example Usage:
import os
from dotenv import load_dotenv

load_dotenv()

API_KEYS = [
    os.environ["GEMINI_KEY_1"],
    os.environ["GEMINI_KEY_2"]
]

model = GeminiProvider(
    API_KEYS
)
try:
    datas: LLmOutput = model.generate(
    "Donne moi une fonction python qui permet d additionner deux nombres")
    if datas is not None:
        print(datas.content)
except LlmError as e:
    print(e)
"""
