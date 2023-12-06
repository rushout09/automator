import sys
import json
import os
import secrets
import requests
from io import StringIO
from typing import Optional
from bs4 import BeautifulSoup

directories = {
    "generated_scripts": "generated_scripts",
    "chat_logs": "chat_logs",
    "usage_logs": "usage_logs"
}


def generate_conversation_id(conversation_id: Optional[str], length=8):
    if conversation_id:
        return conversation_id
    # Generate a random hexadecimal string and return the first 'length' characters
    conversation_id = secrets.token_hex(length // 2)[:length]
    return conversation_id


def init_directories():
    for name, path in directories.items():
        if not os.path.exists(path):
            os.makedirs(path)
            print(f"Directory '{path}' created.")
        else:
            print(f"Directory '{path}' already exists.")


def exec_python_code(user_code: str):
    # Save the user-provided code to a file

    with open(f'{directories.get("generated_scripts")}/user_code.py', 'w') as file:
        file.write(user_code)

    # Redirect stdout and stderr to capture the output
    stdout_backup = sys.stdout
    stderr_backup = sys.stderr
    sys.stdout = StringIO()
    sys.stderr = StringIO()

    try:
        # Execute the user-provided code
        with open('generated_scripts/user_code.py', 'r') as file:
            exec(file.read())
    except Exception as e:
        # Capture any exception and print the error
        print(f"Error: {e}")

    # Retrieve the captured output and error
    stdout_result = sys.stdout.getvalue()
    stderr_result = sys.stderr.getvalue()

    # Restore stdout and stderr
    sys.stdout = stdout_backup
    sys.stderr = stderr_backup

    return stdout_result


def get_cleaned_html(url: str):
    headers = {
        'user-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) '
                      'Chrome/55.0.2883.87 Safari/537.36'}
    response = requests.get(url=url, headers=headers)

    if response.status_code == 200:
        html_content = response.text

        # Parse HTML content with BeautifulSoup
        soup = BeautifulSoup(html_content, 'html.parser')

        # Find all relevant tags
        relevant_tags = soup.find_all(['a', 'span', 'input', 'button'])

        # Extract and print the content of the relevant tags
        relevant_tags_content = ""
        for tag in relevant_tags:
            relevant_tags_content += str(tag)

        final_line = ""
        for line in relevant_tags_content.splitlines():
            if any(["<path" in line, "<svg" in line, "<img" in line]):
                # print(line)
                continue
            final_line += line
        return final_line
    return f"URL returned {response.status_code} response."


def append_conversation(messages: dict, conversation_id: str, message: dict):
    messages[conversation_id].append(message)
    chat_file_path = f'{directories.get("chat_logs")}/{conversation_id}.jsonl'
    with open(chat_file_path, 'w', encoding='utf-8') as f:
        for item in messages[conversation_id]:
            f.write(json.dumps(item, ensure_ascii=False) + '\r\n')


def append_usage(usages: dict, conversation_id: str, usage: dict):
    print("Total token usage in this call\n")
    print('\n'.join([f"{key}: {value}" for key, value in usage.items()]))
    usages[conversation_id].append(usage)
    usage_file_path = f'{directories.get("usage_logs")}/{conversation_id}.jsonl'
    with open(usage_file_path, 'w', encoding='utf-8') as f:
        for item in usages[conversation_id]:
            f.write(json.dumps(item, ensure_ascii=False) + '\r\n')


def get_usages(conversation_id: str):

    usage_file_path = f'{directories.get("usage_logs")}/{conversation_id}.jsonl'

    if os.path.exists(usage_file_path):
        with open(usage_file_path, 'r', encoding='utf-8') as f:
            usages = [json.loads(line) for line in f]
        return usages
    else:
        return None


def get_conversation(conversation_id: str):

    chat_file_path = f'{directories.get("chat_logs")}/{conversation_id}.jsonl'

    if os.path.exists(chat_file_path):
        with open(chat_file_path, 'r', encoding='utf-8') as f:
            messages = [json.loads(line) for line in f]
        return messages
    else:
        return None


print(get_cleaned_html("https://www.joinef.com"))
