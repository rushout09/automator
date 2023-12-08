from dotenv import load_dotenv
from openai import OpenAI, BadRequestError

from utils import *

load_dotenv()
init_directories()
client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

automation_library = "playwright"

system_prompt = f"""
You are a UI Automation Engineer proficient in Python's {automation_library} library.
The user will provide you with a web based workflow that needs to be automated starting with a url.
You need to provide the user with a complete end to end script that can automate the workflow described by the user.
To create the script you need to decompose the workflow and think step by step.

Always use XPath to list all the css selectors containing the text.
When search for selectors by text, make sure you take care of case sensitivity.
From the list of elements, select the correct element to take action on. 
You are given a tool 'exec_python_code'. Use this tool to execute Python code and get the output of the executed code.
Use 'try and except' blocks to catch exceptions in your code and print them.
Add print statements after every action to validate if that line of code worked instead of assuming things.
Add 5 seconds wait times for the pages to load.

Assume {automation_library} is already installed.
Ensure the browser is in headless=False.
Ensure that browser window is maximised. 

Think about the workflow step by step and always follow the sequence of thought, action, and observation flow.
 1. Thought: Think of an action plan and share it with user.
 2. Action: If user says yes then go ahead and call the tool
 3. Observation: Observe the output of the Action step and plan next step.

Respond only with 'TERMINATED' to let user know that script for the workflow is completed.
"""

conversation_id = generate_conversation_id(input("Enter existing Conversation Id or press enter to start a new one."))
print(conversation_id)
messages: dict = {conversation_id: get_conversation(conversation_id=conversation_id) or [{"role": "system",
                                                                                          "content": system_prompt}]}
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
            temperature=0.7,
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
                exec_output = exec_python_code(function_args.get("code_block"), conversation_id=conversation_id)
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
            print(conversation_id)
            break
        user_prompt = input("Suggest\n")
        append_conversation(messages=messages, conversation_id=conversation_id, message={
            "role": "user",
            "content": user_prompt,
        })
        if user_prompt in ["finish", "terminate"]:
            print(conversation_id)
            break

# Todo: Figure out the best way to distribute this.
# Todo: Have another AI agent to review code?
# Todo: Improve prompt.
# Todo: Give the Agent eyes with HTML? This did not work very well.
# Todo: try llava/gpt4v and vision.
