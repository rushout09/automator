import os
import json
from dotenv import load_dotenv
from openai import OpenAI
from run_code import exec_python_code
load_dotenv()

client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))


system_prompt = """
You are a UI Automation Engineer proficient in Python's Playwright library.
The user will provide you with a web browser-based workflow in natural language.
You need to provide the user with a complete end to end python script using playwright library that can automate the workflow described by the user.

Since you will not be aware of the elements and css selectors on the website, you cannot write the script in one go.
To create the script you need to decompose the workflow in multiple steps.
Utilize XPath to find a list of relevant elements and iterate through the list to find the correct element.
Implement 'try and except' blocks where applicable to catch errors and explore different techniques.
Include sufficient print statements to validate if something worked instead of assuming things
You are given a tool 'exec_python_code'. Use this tool to execute Python code and get the output of the executed code.
Assume playwright is already installed.
Ensure the browser is in headless=False mode.

Approach the task step by step and always follow the sequence of thought, action, and observation flow.
 1. Thought: Think of an action plan and share it with user.
 2. Action: If user says yes then go ahead and call the tool
 3. Observation: Observe the output of the Action step and plan next step.

Upon completing the entire workflow, respond only with 'TERMINATED' to let user know the workflow is automated.
"""

messages = [{"role": "system", "content": system_prompt}]

user_prompt = input("Enter the workflow\n")
messages.append({
        "role": "user",
        "content": user_prompt,
    })

while True:
    print("Calling GPT API")
    response = client.chat.completions.create(
        messages=messages,
        model="gpt-4-1106-preview",
        tools=[
            {
                "type": "function",
                "function": {
                    "description": "execute Python code and get the output of the executed code.",
                    "name": "exec_python_code",
                    "parameters": {
                        "type": "object",
                        "properties": {
                            "code_block": {
                                "type": "string",
                                "description": "Python code block to execute",
                            },
                        },
                        "required": ["code_block"],
                    },
                }
            }
        ]
    )

    response_message = response.choices[0].message
    messages.append(response_message)
    gpt_response = response_message.content
    if gpt_response is not None:
        print(gpt_response)
        if gpt_response == "TERMINATED":
            break
        user_prompt = input("Suggest\n")
        messages.append({
            "role": "user",
            "content": user_prompt,
        })
    if response_message.tool_calls is None:
        continue
    for tool_call in response_message.tool_calls:
        function_name = tool_call.function.name
        function_args = json.loads(tool_call.function.arguments)
        print("Execute following code block:")
        print(function_args.get("code_block"))
        print("Paste the output:")
        exec_output, exec_error = exec_python_code(function_args.get("code_block"))
        if exec_error is not None:
            exec_output += exec_error
        print(f"Output: {exec_output}")
        messages.append(
            {
                "tool_call_id": tool_call.id,
                "role": "tool",
                "name": function_name,
                "content": exec_output,
            }
        )

