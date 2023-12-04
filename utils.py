import sys
import json
import os
import secrets
from io import StringIO
from typing import Optional

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

    return stdout_result, stderr_result


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
