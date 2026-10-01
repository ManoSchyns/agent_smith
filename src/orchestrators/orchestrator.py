from src.Llm import LlmError, LLmOutput
from .models import StepMetrics
from src.extraction import extract_code, ExtractError
from src.config import PROVIDER
from src.prompt import get_prompt
from src.sandbox import Sandbox


def orchestrateur(
        type: str,
        prompt: str,
        model_name: str,
        provider_url: str
     ) -> dict:
    """
    Agent's main loop.

    Arguments:
        type (str): The agent type
        prompt: (str): The request made
        model_name (str): The model name
        provider_url (str): The model's API URL
    """
    system_prompt: str = ""
    curr_prompt: str = ""
    steps: list[StepMetrics] = []

    file_path: str = "mcp_tools_mbpp.py"
    if type == "swebench":
        file_path = "mcp_tools_swebench.py"

    try:
        # On charge le model
        model = PROVIDER[provider_url](model_name=model_name)

        # on charge la sandbox
        sandbox = Sandbox(connection_mcp="stdio",
                          url_connection="http://127.0.0.2:8000/mcp",
                          file_path=file_path)

        curr_prompt = get_prompt(sandbox.execute("help"),
                                 prompt)
        system_prompt = curr_prompt
    except (KeyError):
        return {
            "SUCCESS": False,
            "PROMPT": "",
            "OUTPUT": ("The provided URL does not allow "
                       "access to a known model."),
            "STEPS": steps
         }

    except (Exception, LlmError) as e:
        return {
            "SUCCESS": False,
            "PROMPT": "",
            "OUTPUT": str(e),
            "STEPS": steps
         }

    curr_step: int = 1
    retries: int = 0

    finish_text: str = "your code"
    if type == "swebench":
        finish_text = "get_patch()"
    running: bool = True

    try:
        while (running):
            print("here")
            datas: LLmOutput = model.generate(curr_prompt)
            print("\n\n=======LLM output======")
            print(datas.content)
            print("===========\n\n")

            try:
                print("\n\n======= Extracted ==========")
                code = extract_code(datas.content)
                print(code)
                print("===========\n\n")

                print("\n\n======= Sandbox output ==========")
                ret_val = sandbox.execute(code)
                print(ret_val)
                print("===========\n\n")
                if isinstance(ret_val, dict) and "ended" in ret_val.keys():
                    if ret_val["ended"] or ret_val["kill"]:
                        running = False

                curr_prompt += f"\nThe result of the provided code: {code}"
                curr_prompt += f"Is : {ret_val}"
                curr_prompt += ("Don't forget to use "
                                f"final_answer({finish_text})")
                curr_prompt += "If you have finish the Task"

                steps.append(StepMetrics(
                    step=curr_step,
                    input_tokens=datas.total_input_tokens,
                    output_tokens=datas.total_output_tokens,
                    request_time_ms=datas.reponse_time,
                    api_url=provider_url,
                    model_name=model_name,
                    sandbox_input=code,
                    sandbox_output=str(ret_val),
                    retries=retries
                ))
                retries = 0
                curr_step += 1
            except ExtractError as e:
                print("\n\n========== Extraction Error ===========\n\n")
                retries += 1
                curr_prompt += f"\nFor the provided input: {datas.content}"
                curr_prompt += f"Erreur {e}"

        return {
            "SUCCESS": True,
            "PROMPT": system_prompt,
            "OUTPUT": ret_val["stdout"],
            "STEPS": steps
        }

    except (LlmError, Exception) as e:
        return {
            "SUCCESS": False,
            "PROMPT": system_prompt,
            "OUTPUT": str(e),
            "STEPS": steps
        }

    finally:
        sandbox.close()
