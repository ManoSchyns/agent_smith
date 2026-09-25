from src.Llm import LlmError, LLmOutput
from src.extraction import extract_code, ExtractError
from src.config import PROVIDER
from src.prompt import get_prompt
from sandbox import Sandbox


"""
Exemple de fonctionnement d un agent
"""


def agent_example(prompt: str, model_name: str, provider_url: str) -> None:
    try:
        # On charge le model
        model = PROVIDER[provider_url](model_name=model_name)

        # on charge la sandbox
        sandbox = Sandbox(config="config.json",
                          connection_mcp="stdio",
                          url_connection="http://127.0.0.3:8000/mcp",
                          file_path="mcp_tools_mbpp.py")

        running = True
        curr_prompt = get_prompt(sandbox.execute("help"),
                                 prompt)
        while (running):
            datas = model.generate(curr_prompt)

            try:
                code = extract_code(datas.content)
                print(f"======llm tried : {code}\n\n")
                ret_val = sandbox.execute(code)
                if isinstance(ret_val, dict) and "ended" in ret_val.keys():
                    if ret_val["ended"] or ret_val["kill"]:
                        running = False

                curr_prompt += f"\nThe result of the provided code: {code}"
                curr_prompt += f"Is : {ret_val}"
            except ExtractError as e:
                curr_prompt += f"\nFor the provided input: {datas.content}"
                curr_prompt += f"Erreur {e}"
        print("\n===========\nenddddd\n=================\n")
        print(ret_val["stdout"])
                 

    except (LlmError, ExtractError) as e:
        print(e)
    except (KeyError):
        print("The provided URL does not allow access to a known model.")
    except Exception as e:
        print(e)
    finally:
            sandbox.close()

if __name__ == "__main__":
    agent_example("Write a function to check whether it follows the sequence given in the patterns array.,def is_samepatterns(colors, patterns):",
                  "gemini-3.5-flash-lite",
                  "https://generativelanguage.googleapis.com")