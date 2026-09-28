from src.Llm import LlmError, LLmOutput
from src.extraction import extract_code, ExtractError
from src.config import PROVIDER
from src.prompt import get_prompt
from src.sandbox import Sandbox


def orchestrateur(prompt: str, model_name: str, provider_url: str) -> str:
    try:
        # On charge le model
        model = PROVIDER[provider_url](model_name=model_name)

        # on charge la sandbox
        sandbox = Sandbox(connection_mcp="stdio",
                          url_connection="http://127.0.0.2:8000/mcp",
                          file_path="mcp_tools_mbpp.py")

        running = True
        curr_prompt = get_prompt(sandbox.execute("help"),
                                 prompt)
        while (running):
            print("Common")
            datas = model.generate(curr_prompt)

            try:
                code = extract_code(datas.content)
                print("Common2")
                ret_val = sandbox.execute(code)
                if isinstance(ret_val, dict) and "ended" in ret_val.keys():
                    if ret_val["ended"] or ret_val["kill"]:
                        running = False

                curr_prompt += f"\nThe result of the provided code: {code}"
                curr_prompt += f"Is : {ret_val}"
            except ExtractError as e:
                curr_prompt += f"\nFor the provided input: {datas.content}"
                curr_prompt += f"Erreur {e}"
            print("Common3")

        return ret_val["stdout"]
                 

    except (LlmError, ExtractError) as e:
        return str(e)
    except (KeyError):
        return ("The provided URL does not allow access to a known model.")
    except Exception as e:
        return str(e)
    finally:
            sandbox.close()
