from Llm import LlmError, LLmOutput
from extraction import extract_code, ExtractError
import fire
from config import PROVIDER

"""
Exemple de fonctionnement d un agent
"""


def agent_example(prompt: str, model_name: str, provider_url: str) -> None:
    try:

        model = PROVIDER[provider_url](model_name=model_name)
        datas: LLmOutput = model.generate(prompt)
        print(extract_code(datas.content))

    except (LlmError, ExtractError) as e:
        print(e)
    except (KeyError):
        print("The provided URL does not allow access to a known model.")


if __name__ == "__main__":
    fire.Fire(
        {
            "agent_example": agent_example
        },
        name="Agent Smith"
    )
