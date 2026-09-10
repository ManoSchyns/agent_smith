from dotenv import load_dotenv
from typing import Callable
from functools import partial
from Llm import GeminiProvider, OpenRouterProvider
import os


load_dotenv()

GEMINI_API_KEYS = [
    os.environ["GEMINI_KEY_1"],
    os.environ["GEMINI_KEY_2"]
]

OPEN_ROUTER_API_KEYS = [
    os.environ["OPEN_ROUTER_KEY_1"],
    os.environ["OPEN_ROUTER_KEY_2"],
    os.environ["OPEN_ROUTER_KEY_3"],
    os.environ["OPEN_ROUTER_KEY_4"],
    os.environ["OPEN_ROUTER_KEY_5"],
    os.environ["OPEN_ROUTER_KEY_6"]
]

PROVIDER: dict[str, Callable] = {
    "https://generativelanguage.googleapis.com": partial(
            GeminiProvider, api_keys=GEMINI_API_KEYS
        ),

    "https://openrouter.ai/api/v1/chat/completions": partial(
            OpenRouterProvider, api_keys=OPEN_ROUTER_API_KEYS
        )
}
