import requests
import time


# Global variable to store the token and its expiration time
token_info = {
    "token": None,
    "expiration_time": None
}

# Function to create a new base token
def create_token(mcp):
    global token_info
    url = f"https://{mcp}/tron/api/v2/tokens"
    payload = {
        "username": "admin",
        "password": "adminpw",
        "timeout": 3600  # Token expiration in seconds
    }
    headers = {
        "Content-Type": "application/x-www-form-urlencoded"
    }

    try:
        response = requests.post(url, data=payload, headers=headers, verify=False)
        if response.status_code == 201:
            token_data = response.json()
            token_info["token"] = token_data.get("token")
            token_info["expiration_time"] = time.time() + payload["timeout"]
            print("Token created successfully!")
        else:
            print(f"Failed to create token: {response.status_code}, {response.text}")
    except requests.RequestException as e:
        print(f"Error creating token: {e}")

# Function to check if the token is valid
def is_token_valid():
    global token_info
    if token_info["token"] and token_info["expiration_time"]:
        return time.time() < token_info["expiration_time"]
    return False

# Function to get a valid token
def get_token(mcp):
    if is_token_valid():
        return token_info["token"]
    create_token(mcp)
    return token_info["token"]


# Example API Call: Retrieve Scripts
mcp="10.92.44.121"
API_URL = f"https://{mcp}/configmgmt/api/v1/customScripts/execute"
token = get_token(mcp)
headers = {
    "Authorization": f"Bearer {token}",
    "accept": "application/json"
}

# Script Execution Payload
# Payload for the API Request
payload = {
    "operation": "run",
    "scripts": [
        {
            "scriptName": "cliCutThrough",
            "inputs": [
                {
                    "cmdFile": "ShutOffInactivityTimer",
                    "scriptAttributes": {},
                    "protocolType": "cli"
                }
            ]
        }
    ],
    "included": [
        {
            "id": "PE-6x",
            "type": "connectionAttributes",
            "attributes": {
                "neName": "PE-6x",
                "neType": "3928",
                "typeGroup": "PN6x"
            }
        }
    ]
}

# Execute the Script
try:
    response = requests.post(API_URL, json=payload, headers=headers, verify=False)

    # Check the Response
    if response.status_code == 200:
        print("Script executed successfully!")
        print("Response:", response.json())
    else:
        print(f"Failed to execute script. HTTP Status Code: {response.status_code}")
        print("Error:", response.text)
except requests.RequestException as e:
    print(f"Error during API call: {e}")