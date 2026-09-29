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
     ) -> tuple[str, str,
                list[StepMetrics]]:
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

    try:
        # On charge le model
        model = PROVIDER[provider_url](model_name=model_name)

        # on charge la sandbox
        sandbox = Sandbox(connection_mcp="stdio",
                          url_connection="http://127.0.0.2:8000/mcp",
                          file_path="mcp_tools_mbpp.py")

        curr_prompt = get_prompt(sandbox.execute("help"),
                                 prompt)
        system_prompt = curr_prompt
    except (KeyError):
        return ("",
                "The provided URL does not allow access to a known model.",
                steps)
    except (LlmError) as e:
        return ("", str(e), steps)

    except Exception as e:
        return ("", str(e), steps)

    curr_step: int = 1
    retries: int = 0

    finish_text: str = "your code"
    if type == "swebench":
        finish_text = "get_patch()"
    running: bool = True

    try:
        while (running):
            datas: LLmOutput = model.generate(curr_prompt)
            print(datas.content)

            try:
                code = extract_code(datas.content)

                ret_val = sandbox.execute(code)
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
                retries += 1
                curr_prompt += f"\nFor the provided input: {datas.content}"
                curr_prompt += f"Erreur {e}"

        return (system_prompt, "SUCCESS", steps)

    except (LlmError) as e:
        return (system_prompt, str(e), steps)
    except Exception as e:
        return (system_prompt, str(e), steps)
    finally:
        sandbox.close()
