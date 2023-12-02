import os
from dotenv import load_dotenv
from openai import OpenAI
load_dotenv()

client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))


system_prompt = ("You are a UI Automation Engineer. You are very proficient in Python's Playwright library. "
                 "User will give you a sequence of steps in a testcase to perform on a browser. "
                 "Your task is to think step by step and generate playwright commands and give it to user to execute."
                 "Manually create and manage the playwright event loop"
                 "Ask the User for the result of the previous command and use it to plan your next command."
                 "You do not know the html element name or css selector, so you must use generic xpath and try to find most relevant element from list of elements possible."
                 "Always follow the sequence of Thought, Action, Observation"
                 "Let the browser be in headless=False mode"
                 "Once the sequence of steps is completed, reply only with TERMINATED")

messages = [{"role": "system", "content": system_prompt}]

gpt_response = ""

while gpt_response != "TERMINATED":
    if gpt_response != "":
        messages.append({
            "role": "assistant",
            "content": gpt_response
        })
        user_prompt = input(gpt_response)
    else:
        user_prompt = input("Enter the testcase")
    messages.append({
        "role": "user",
        "content": user_prompt,
    })
    chat_completion = client.chat.completions.create(
        messages=messages,
        model="gpt-4-1106-preview",
    )
    gpt_response = chat_completion.choices[0].message.content
