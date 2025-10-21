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

import requests

def get_job_status(mcp, base_url, job_id):
    """
    Query the API and parse the response to extract the status for jobResults.
    
    :param base_url: The base URL of the API endpoint.
    :param job_id: The job ID to append to the URL.
    :return: The status of jobResults if available, otherwise None.
    """
    # Construct the full URL
    url = f"{base_url}/{job_id}"
    token = get_token(mcp)
    headers = {
        "Authorization": f"Bearer {token}",
        "accept": "application/json"
    }

    try:
        # Make the GET request
        response = requests.get(url, headers=headers, verify=False)
        
        # Check if the request was successful
        if response.status_code == 200:
            # Parse the JSON response
            response_json = response.json()
            
            # Navigate to the 'output' -> 'data' -> 'attributes' -> 'scriptResults' -> 'status'
            output_data = response_json.get("output", {}).get("data", {}).get("attributes", {}).get("scriptResults", [])
            
            # Extract the status of the first script result (if available)
            if output_data and isinstance(output_data, list):
                status = output_data[0].get("status")
                return status
            else:
                print("No script results found in the response.")
                return None
        else:

            print(f"Failed to fetch data. HTTP Status Code: {response.status_code}")
            return None
    except Exception as e:
        print(f"An error occurred: {e}")
        return None

def execute_custom_script(mcp, device, cmd_file, script_attributes, devices):
    """
    Executes a custom script on the specified MCP using the provided command file and attributes.
    
    Args:
        mcp (str): IP address of the MCP.
        cmd_file (str): Command file to execute.
        script_attributes (dict): Attributes for the script execution.

    # Example API Call: Retrieve Scripts
    mcp="10.92.44.121"
    # Script Parameters and Payload
    cmd_file = "ApplyLP3903BaseCAL"  # Replace with the desired script command file
    script_attributes = {
        "NTP_SERVER": "10.92.44.131",  # Replace with your NTP server
        "HOSTNAME": "BARB-6x",         # Replace with your hostname
        "MCP_IP_ADDRESS": "10.92.44.121"  # Replace with your MCP IP address
    }

"""
    API_URL = f"https://{mcp}/configmgmt/api/v1/customScripts/execute"
    token = get_token(mcp)
    headers = {
        "Authorization": f"Bearer {token}",
        "accept": "application/json"
    }
    neTypeGroup = devices[device]['attributes']['typeGroup']
    if neTypeGroup == "PN6x":
        protocolType = "cli"
        scriptName = "cliCutThrough"
    else:
        protocolType = "netconf"
        scriptName = "netconfCutThrough"
        

    # Payload for the API Request
    payload = {
        "operation": "run",
        "scripts": [
            {
                "scriptName": scriptName,
                "inputs": [
                    {
                        "cmdFile": cmd_file,
                        "scriptAttributes": script_attributes,
                        "protocolType": protocolType
                    }
                ]
            }
        ],
        "included": [
            {
                "id": device,
                "type": "connectionAttributes",
                "attributes": {
                    "neName": device,
                    "neType": devices[device]['attributes']['neType'],
                    "typeGroup": devices[device]['attributes']['typeGroup']
                }
            }
        ]
    }

    # Execute the Script
    try:
        response = requests.post(API_URL, json=payload, headers=headers, verify=False)
        response_json = response.json()
        job_id = response_json.get("jobId")


        # Check the Response
        if response.status_code == 200:
            print("Script executed successfully!")
            print(f"jobId: for device: {device} Script: {cmd_file} is {job_id}")
            # status_url = f"https://{mcp}/configmgmt/api/v1/scriptExecutionDetails"
            # https://10.92.44.121/configmgmt/api/v1/neMaintenanceDetails?limit=200&networkConstructType=aggregatedNetworkElement,networkElement&offset=0
            # time.sleep(5)  # Simulate sleep
            # get_job_status(mcp, status_url, job_id)
        else:
            print(f"Failed to execute script. HTTP Status Code: {response.status_code}")
            print("Error:", response.text)
    except requests.RequestException as e:
        print(f"Error during API call: {e}")