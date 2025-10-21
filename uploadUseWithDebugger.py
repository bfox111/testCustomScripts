#!/usr/bin/env python

"""
Author: Barbara A. Fox <bfox@ciena.com>

Upload custom scripts to a particular Navigator.

Lots of help from Harry Solomou and chatGPT.
"""

import sys
import requests
import time
import os

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

def upload_script(mcp, productType, protocolType, scriptName, description, file_path):
    """
    Upload a custom script to Navigator.
    """
    url = f"https://{mcp}/configmgmt/api/v1/customScripts"
    token = get_token(mcp)
    headers = {
        "Authorization": f"Bearer {token}",
        "accept": "application/json"
    }

    data = {
        "typeGroup": productType,
        "protocolType": protocolType,
        "scriptName": scriptName,
        "description": description
    }

    try:
        if not os.path.exists(file_path):
            print(f"File not found: {file_path}")
            return

        with open(file_path, "rb") as file:
            # Match multipart/form-data structure from curl
            files = {
                "file": (os.path.basename(file_path), file, "text/plain")
            }
            response = requests.post(url, headers=headers, data=data, files=files, verify=False)

            # Print the response body for debugging
#            print(f"Response Body: {response.text}")

            if response.status_code in [200, 201]:  # Adjusted success check
                print(f"Custom Script '{scriptName}' uploaded successfully!")
            else:
                print(f"Failed to upload script '{scriptName}': {response.status_code}, {response.text}")
    except requests.RequestException as e:
        print(f"Error uploading script '{scriptName}': {e}")
        
        
def main():
    """
    Main function to process scripts file and upload each script.
    """
    mcp_ip = '10.92.44.121'
    scripts_file = "/mnt/c/Users/bfox/OneDrive - Ciena Corporation/Documents/Customers/Lightpath/NCS-Customize/uploadCustomScripts.txt"

    try:
        if not os.path.exists(scripts_file):
            print(f"Scripts file not found: {scripts_file}")
            return

        with open(scripts_file, 'r') as scripts:
            for line in scripts:
                parsed_line = line.strip().split(',')
                if len(parsed_line) < 4:
                    print(f"Invalid line format: {line}")
                    continue

                name = parsed_line[0].strip()
                productType = parsed_line[1].strip()
                protocolType = parsed_line[2].strip()
                file_path = parsed_line[3].strip()
                description = parsed_line[4].strip() if len(parsed_line) > 4 else ""

                upload_script(mcp_ip, productType, protocolType, name, description, file_path)
                time.sleep(2)  # Optional delay between uploads
    except Exception as e:
        print(f"Error processing scripts file: {e}")

if __name__ == "__main__":
    main()