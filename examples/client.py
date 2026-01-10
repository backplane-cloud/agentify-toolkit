# Copyright Backplane 2026
# Author: Lewis Sheridan
# Description: Simple Demo to use Agentify Library to create an AI Agent

import requests

def main():

    # Set the URL endpoint
    endpoint = "http://127.0.0.1:8001/prompt"

    # Create prompt in JSON
    prompt = {"question": "Which AI model are you in 5 words"}

    # Post request
    response = requests.post(endpoint, json=prompt)

    if response.status_code == 200:
        data = response.json()
        print("Response", data)
    else:
        print(f"Request failed with status {response.status_code}: {response.text}")

if __name__ == "__main__":
    main()