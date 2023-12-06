from dotenv import load_dotenv
from openai import OpenAI, BadRequestError

from utils import *

load_dotenv()
init_directories()
client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

system_prompt = ["""
You are a UI Automation Engineer proficient in Python's Playwright library.
The user will provide you with a web browser-based workflow in natural language.
You need to provide the user with a complete end to end script that can automate the workflow described by the user.

Since you will not be aware of the elements and css selectors on the website, you cannot write the script in one go.
To create the script you need to decompose the workflow in multiple steps.
Utilize XPath to find a list of relevant elements and iterate through the list to find the correct element.
Implement 'try and except' blocks where applicable to catch errors and explore different techniques.
Include sufficient print statements to validate if something worked instead of assuming things.
Add sufficient wait times for the pages to load.
You are given a tool 'exec_python_code'. Use this tool to execute Python code and get the output of the executed code.
Assume playwright is already installed.
Ensure the browser is in headless=False mode. 

Approach the task step by step and always follow the sequence of thought, action, and observation flow.
 1. Thought: Think of an action plan and share it with user.
 2. Action: If user says yes then go ahead and call the tool
 3. Observation: Observe the output of the Action step and plan next step.

Upon completing the entire workflow, respond only with 'TERMINATED' to let user know the workflow is automated.
""",
                 """
You are a UI Automation Agent proficient in Python's Playwright library.
The user will provide you with a web browser-based testcase in natural language.
You need to provide the user with a complete end to end script that can automate the testcase described by the user.
Since you will not be aware of the css selectors on the webpage, you cannot write the script in one go.
To create the script you need to decompose the user's workflow in multiple steps.
You are given a tool 'exec_python_code'. Use this tool to execute Python code and get the output of the executed code.

Steps to accomplish your task:
- Navigate to the initial webpage suggested by the user.
- You can get a filtered html content of the webpage by using the tool 'get_cleaned_html'.
- Use this html and Xpath to find a list of relevant CSS Selectors and iterate through it to find the correct element.
- Once you are able to locate an html element, you can use it to perform actions as per user's workflow.
- Implement 'try and except' blocks where applicable to catch errors and explore different techniques.
- Include sufficient print statements to validate if something worked instead of assuming things.
- Add 'sleep' time of 10 seconds after every action.
- Assume playwright is already installed.
- Ensure the browser is in headless=False mode.
- Properly concatenate the script for each step and execute the whole script to validate if the full workflow is working as intended. 

Be Creative and think out of the box.

Approach the task step by step and always follow the sequence of thought, action, and observation flow.
 1. Thought: Think of an action plan and share it with user.
 2. Action: If user says yes then go ahead and call the tool
 3. Observation: Observe the output of the Action step and plan next step.

Upon completing the entire workflow, respond only with 'TERMINATED' to let user know the workflow is automated.
"""]

conversation_id = generate_conversation_id(input("Enter existing Conversation Id or press enter to start a new one."))
messages: dict = {conversation_id: get_conversation(conversation_id=conversation_id) or [{"role": "system",
                                                                                          "content": system_prompt[0]}]}
usages: dict = {conversation_id: get_usages(conversation_id=conversation_id) or []}

user_prompt = input("Enter the workflow\n")
append_conversation(messages=messages, conversation_id=conversation_id, message={
    "role": "user",
    "content": user_prompt,
})

while True:
    print("Calling GPT API")
    try:
        response = client.chat.completions.create(
            messages=messages[conversation_id],
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
                },
                # {
                #     "type": "function",
                #     "function": {
                #         "description": "Removes unnecessary tags from a webpage and returns cleaned html as a string",
                #         "name": "get_cleaned_html",
                #         "parameters": {
                #             "type": "object",
                #             "properties": {
                #                 "url": {
                #                     "type": "string",
                #                     "description": "URL of the webpage to get cleaned html",
                #                 },
                #             },
                #             "required": ["url"],
                #         },
                #     }
                # }
            ]
        )
    except BadRequestError as e:
        print(
            messages)  # We get error when the previous message by assistant contains both message and tool_call.
        raise e

    response_message = response.choices[0].message
    append_usage(usages=usages, conversation_id=conversation_id, usage=response.usage.model_dump())
    append_conversation(messages=messages, conversation_id=conversation_id,
                        message=response_message.model_dump(exclude_none=True))
    gpt_response = response_message.content
    if response_message.tool_calls is not None:
        for tool_call in response_message.tool_calls:
            function_name = tool_call.function.name
            if function_name == "exec_python_code":
                function_args = json.loads(tool_call.function.arguments)
                print("Execute following code block:")
                print(function_args.get("code_block"))
                exec_output = exec_python_code(function_args.get("code_block"))
                print(f"Output: {exec_output}")
                append_conversation(messages=messages, conversation_id=conversation_id,
                                    message={
                                        "tool_call_id": tool_call.id,
                                        "role": "tool",
                                        "name": function_name,
                                        "content": exec_output,
                                    })
            else:
                function_args = json.loads(tool_call.function.arguments)
                print("Get the cleaned html for following URL:")
                print(function_args.get("url"))
                exec_output = get_cleaned_html(url=function_args.get("url"))
                print(f"Output: {exec_output}")
                append_conversation(messages=messages, conversation_id=conversation_id,
                                    message={
                                        "tool_call_id": tool_call.id,
                                        "role": "tool",
                                        "name": function_name,
                                        "content": exec_output,
                                    })

    if gpt_response is not None:
        print(gpt_response)
        if gpt_response == "TERMINATED":
            break
        user_prompt = input("Suggest\n")
        append_conversation(messages=messages, conversation_id=conversation_id, message={
            "role": "user",
            "content": user_prompt,
        })
        if user_prompt in ["finish", "terminate"]:
            break

# Todo: Figure out the best way to distribute this.
# Todo: Have another AI agent to review code?
# Todo: Give the Agent eyes with HTML?
# Todo: try opencv and vision.
