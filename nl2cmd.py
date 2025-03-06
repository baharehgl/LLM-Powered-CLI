
import os
import sys
import platform
import openai

# 1. API Key setup: Get the API key from an environment variable.
openai.api_key = os.getenv("OPENAI_API_KEY")
if openai.api_key is None:
    print("Error: OpenAI API key not found. Set the OPENAI_API_KEY environment variable.")
    sys.exit(1)

# 2. Get the natural language query from command-line arguments.
if len(sys.argv) < 2:
    print("Usage: nl2cmd.py \"<natural language instruction>\"")
    sys.exit(1)
user_query = " ".join(sys.argv[1:])

# 3. Detect the operating system.
os_name = platform.system()  # e.g., "Windows" or "Linux"

# 4. Prepare the OpenAI Chat API request.
# The system message instructs the model to output only a single, safe command.
system_message = (
    "You are a helpful assistant that translates a user's natural language request into a single OS command. "
    f"The current operating system is {os_name}. "
    "Only output the command itself, without any explanation or extra text. "
    "Never return commands that could be destructive or harmful."
)
messages = [
    {"role": "system", "content": system_message},
    {"role": "user", "content": user_query}
]

try:
    response = openai.ChatCompletion.create(
        model="gpt-3.5-turbo",
        messages=messages,
        temperature=0  # Deterministic output
    )
except Exception as e:
    print(f"Error calling OpenAI API: {e}")
    sys.exit(1)

command_output = response.choices[0].message.content.strip()

# 5. Implement a basic safety filter to block potentially dangerous commands.
dangerous_substrings = [
    "rm -rf",      # Linux destructive command
    "format c:",   # Windows destructive command
    "mkfs",        # Filesystem creation command
    ":(){",        # Bash fork bomb pattern
    "del /s",      # Windows recursive delete
    "del /q",      # Windows quiet delete
    "shutdown",    # Shutdown command (could be dangerous in some contexts)
    "reboot"       # Reboot command
]
lower_cmd = command_output.lower()
if any(pattern in lower_cmd for pattern in dangerous_substrings):
    print(f"[Blocked] The suggested command '{command_output}' looks unsafe or destructive. Please refine your request.")
    sys.exit(1)

# 6. Print the resulting command.
print(command_output)
