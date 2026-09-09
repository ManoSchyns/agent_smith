from .llm_provider_model import LLmOutput, LlmError
from utils import current_milli_time
import requests
import json


class OpenRouterProvider:
    """
    LLM OpenRouter
    """

    def __init__(self, api_keys: list[str],
                 model_name: str = "openrouter/free",
                 url: str = "https://openrouter.ai/api/v1/chat/completions"
                 ) -> None:
        """
        OpemRouter Argument Initialization

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

    def use_next_key(self) -> bool:
        """
        Move to the next API key, generate the corresponding model
        """
        if self.curr_id == self.max_id - 1:
            return False

        self.curr_id += 1
        return True

    def generate(self, prompt: str) -> LLmOutput:
        """
        Method for generating model output based on a request.
        It makes a request to the API

        Argument:
            prompt(str): The request

        Return:
            (LLmOutput): The AI ​​output
        """
        start_time: float = current_milli_time()

        try:
            reponse = requests.post(
                url=self.url,
                headers={
                    "Authorization": f"Bearer {self.api_keys[self.curr_id]}",
                    "Content-Type": "application/json",
                },
                data=json.dumps({
                    "model": self.model_name,
                    "messages": [
                    {
                        "role": "user",
                        "content": prompt
                    },
                    ],
                    "reasoning": {"enabled": True}
                })
                )
            reponse.raise_for_status()
            content = reponse.json()
        except requests.HTTPError as e:
            if self.use_next_key():
                return self.generate(prompt)
            raise LlmError(e)

        return LLmOutput(
            content=content["choices"][0]["message"]["content"],
            reponse_time=start_time - current_milli_time(),
            total_input_tokens=content["usage"]["prompt_tokens"],
            total_output_tokens=content["usage"]["completion_tokens"],
            api_url=self.url,
            model_name=content["model"]
        )

[{'index': 0, 'logprobs': None, 'finish_reason': 'stop', 'native_finish_reason': 'stop', 'message': {'role': 'assistant', 'content': '```python\ndef additionner(a, b):\n    return a + b\n\nprint(additionner(2, 3))  # Affiche 5\n```', 'refusal': None, 'reasoning': 'We need answer in French likely. User asks "Donne moi une fonction python qui permet d additionner deux nombres" Need provide simple function. No need tools. Ensure maybe mention usage. Final concise.\n', 'reasoning_details': [{'type': 'reasoning.text', 'text': 'We need answer in French likely. User asks "Donne moi une fonction python qui permet d additionner deux nombres" Need provide simple function. No need tools. Ensure maybe mention usage. Final concise.\n', 'format': 'unknown', 'index': 0}]}}]