from Llm import GeminiProvider, LlmError, LLmOutput

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
