from Llm import GeminiProvider, LlmError, LLmOutput, OpenRouterProvider

import os
from dotenv import load_dotenv

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

model_1 = GeminiProvider(
    OPEN_ROUTER_API_KEYS,
    model_name="nex-agi/nex-n2.5-mini:free"
)

model = OpenRouterProvider(
    OPEN_ROUTER_API_KEYS,
    model_name="nex-agi/nex-n2.5-mini:free"
)
try:
    datas: LLmOutput = model.generate(
        "Donne moi une fonction python qui permet d additionner deux nombres")
    if datas is not None:
        print(datas.content)
except LlmError as e:
    print(e)
