import sys
from io import StringIO


def exec_python_code(user_code: str):
    # Save the user-provided code to a file
    with open('generated_scripts/user_code.py', 'w') as file:
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


# Example usage:
# user_code = """
# print("Hello, world!")
# x = 10 / 0  # This will cause an exception
# """
# stdout_result, stderr_result = exec_python_code(user_code)
#
# print("=== Standard Output ===")
# print(stdout_result)
#
# print("=== Standard Error ===")
# print(stderr_result)
