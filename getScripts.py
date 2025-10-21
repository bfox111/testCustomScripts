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
scripts_url = f"https://{mcp}/configmgmt/api/v1/scripts"
token = get_token(mcp)
headers = {
    "Authorization": f"Bearer {token}",
    "accept": "application/json"
}

response = requests.get(scripts_url, headers=headers, verify=False)

if response.status_code == 200:
    print("Raw Response:", response.json())  # Print the raw response
    scripts = response.json()
    print("Available Scripts:")
    for script in scripts.get("scripts", []):  # Adjust based on actual response structure
        print(f"Script Name: {script['scriptName']}, Script : {script['description']}")
else:
    print("Failed to retrieve scripts.")
    print("Error:", response.text)
