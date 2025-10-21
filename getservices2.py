import requests
import time

# Global variable to store the token and its expiration time
token_info = {
    "token": None,
    "expiration_time": None
}

# Function to create a new base token
def create_token():
    global token_info
    url = "https://10.139.8.84/tron/api/v2/tokens"
    payload = {
        "username": "admin",
        "password": "adminpw",
        "timeout": 3600  # Optional, token expiration in seconds
    }
    headers = {
        "Content-Type": "application/x-www-form-urlencoded"
    }

    response = requests.post(url, data=payload, headers=headers, verify=False)  # SSL verification bypassed
    print("Token Response Status:", response.status_code)
    print("Token Response Body:", response.text)
    if response.status_code == 201:
        token_data = response.json()
        token_info["token"] = token_data.get("token")  # Use "token" from response
        token_info["expiration_time"] = time.time() + payload["timeout"]
        print("Token created successfully!")
    else:
        print("Failed to create token:", response.status_code, response.text)

# Function to check if the token is valid
def is_token_valid():
    global token_info
    if token_info["token"] and token_info["expiration_time"]:
        current_time = time.time()
        return current_time < token_info["expiration_time"]
    return False

# Function to get a valid token
def get_token():
    if is_token_valid():
        print("Token is valid!")
        return token_info["token"]
    else:
        print("Token is invalid or expired. Creating a new one...")
        create_token()
        return token_info["token"]

# Function to get all optical services
def get_optical_services():
    token = get_token()
    print("Token:", token)  # Debugging: Print the token
    url = "https://10.139.8.84/perfg/api/channelmargins"
    headers = {
        "Authorization": f"Bearer {token}"
    }
    response = requests.get(url, headers=headers, verify=False)  # SSL verification bypassed
    print("Optical Services Response Status:", response.status_code)
    print("Optical Services Response Body:", response.text)
    if response.status_code == 200:
        optical_services = response.json()
        print("Optical Services retrieved successfully!")
        return optical_services
    else:
        print("Failed to retrieve optical services:", response.status_code, response.text)
        return None

# Example usage
optical_services = get_optical_services()
print("Optical Services:", optical_services)