#!/usr/bin/env python3
import os
import sys
import platform
import openai

# 1. API Key setup
openai.api_key = os.getenv("OPENAI_API_KEY")
if openai.api_key is None:
    print("Error: OpenAI API key not found. Set the OPENAI_API_KEY environment variable.")
    sys.exit(1)

# 2. Get user input from command-line arguments
if len(sys.argv) < 2:
    print("Usage: nl2cmd.py \"<natural language instruction>\"")
    sys.exit(1)
user_query = " ".join(sys.argv[1:])

# 3. Detect OS
os_name = platform.system()

# 4. Prepare OpenAI API request
system_message = (
    "You are a helpful assistant that translates a user's natural language request into a single OS command. "
    f"The current operating system is {os_name}. "
    "Only output the command itself, without any extra explanation. "
    "Never return commands that could be destructive or harmful."
)
messages = [
    {"role": "system", "content": system_message},
    {"role": "user", "content": user_query}
]

try:
    response = openai.ChatCompletion.create(model="gpt-3.5-turbo", messages=messages, temperature=0)
except Exception as e:
    print(f"Error calling OpenAI API: {e}")
    sys.exit(1)

command_output = response.choices[0].message.content.strip()

# 5. Safety check on the generated command
dangerous_substrings = ["rm -rf", "format c:", "format c:", "mkfs", "del /s", "del /q", "shutdown", "reboot"]
lower_cmd = command_output.lower()
if any(pattern in lower_cmd for pattern in dangerous_substrings):
    print(f"[Blocked] The suggested command '{command_output}' looks unsafe or destructive. Refine your request.")
    sys.exit(1)

# 6. Print the resulting command (no auto-execution)
print(command_output)
