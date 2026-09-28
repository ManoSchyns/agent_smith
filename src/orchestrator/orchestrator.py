from src.Llm import LlmError, LLmOutput
from .models import SolutionOutput, StepMetrics
from src.extraction import extract_code, ExtractError
from src.config import PROVIDER
from src.prompt import get_prompt
from src.sandbox import Sandbox


def orchestrateur(prompt: str, model_name: str, provider_url: str) -> tuple[str ,
                                                                            list[StepMetrics]]:
    try:
        print("2")
        steps: list[StepMetrics] = []
        curr_step = 1
        retries: int = 0

        # On charge le model
        model = PROVIDER[provider_url](model_name=model_name)

        # on charge la sandbox
        sandbox = Sandbox(connection_mcp="stdio",
                          url_connection="http://127.0.0.2:8000/mcp",
                          file_path="mcp_tools_mbpp.py")

        running = True
        curr_prompt = get_prompt(sandbox.execute("help"),
                                 prompt)
        system_prompt = curr_prompt
        while (running):
            print("3")
            datas: LLmOutput = model.generate(curr_prompt)
            print("4")

            try:
                code = extract_code(datas.content)

                ret_val = sandbox.execute(code)
                if isinstance(ret_val, dict) and "ended" in ret_val.keys():
                    if ret_val["ended"] or ret_val["kill"]:
                        running = False

                curr_prompt += f"\nThe result of the provided code: {code}"
                curr_prompt += f"Is : {ret_val}"

                steps.append(StepMetrics(step=curr_step,
                                        input_tokens=datas.total_input_tokens,
                                        output_tokens=datas.total_output_tokens,
                                        request_time_ms=datas.reponse_time,
                                        api_url=provider_url,
                                        model_name=model_name,
                                        sandbox_input=code,
                                        sandbox_output=str(ret_val),
                                        retries=retries))
                retries = 0
                curr_step += 1
            except ExtractError as e:
                retries += 1
                curr_prompt += f"\nFor the provided input: {datas.content}"
                curr_prompt += f"Erreur {e}"

        print("4")
        return (system_prompt, "SUCCESS", steps)    

    except (LlmError) as e:
        return (system_prompt, str(e), steps) 
    except (KeyError):
        return (system_prompt,
                "The provided URL does not allow access to a known model.",
                steps)
    except Exception as e:
        return (system_prompt, str(e), steps)
    finally:
            sandbox.close()
