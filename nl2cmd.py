#!/usr/bin/env python3
import os
import sys
import platform
import openai

def generate_command(user_query, os_name):
    # Prepare the OpenAI Chat API request.
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
        return None

    command_output = response.choices[0].message.content.strip()

    # Safety filter to block potentially dangerous commands.
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
        return None

    return command_output

def main():
    # API Key setup: Get the API key from an environment variable.
    openai.api_key = os.getenv("OPENAI_API_KEY")
    if openai.api_key is None:
        print("Error: OpenAI API key not found. Please set the OPENAI_API_KEY environment variable.")
        sys.exit(1)

    # Detect the operating system.
    os_name = platform.system()  # e.g., "Windows" or "Linux"

    # Print initial instructions for the user.
    print("Welcome to the LLM-Powered CLI Command Generator!")
    print("Instructions:")
    print(" - Type a natural language command (e.g., 'list all files including hidden ones') and press Enter.")
    print(" - The tool will output the corresponding OS command for your system.")
    print(" - Type 'exit' (without quotes) to quit the program.\n")

    # Interactive loop
    while True:
        user_query = input("What command would you like me to give you? ")
        if user_query.strip().lower() == "exit":
            print("Exiting. Goodbye!")
            break
        if not user_query.strip():
            # If user enters an empty command, re-prompt.
            continue

        command = generate_command(user_query, os_name)
        if command:
            print("\nSuggested Command:")
            print(command + "\n")

if __name__ == "__main__":
    main()
