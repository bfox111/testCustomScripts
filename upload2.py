#!/usr/bin/env python

"""
Author: Barbara A. Fox <bfox@ciena.com>

Upload custom scripts to a particular Navigator.

Lots of help from Harry Solomou And ChatGPT!
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

def create_token(mcp):
    """
    Create a new base token for authentication.
    """
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
        response.raise_for_status()
        token_data = response.json()
        token_info["token"] = token_data.get("token")
        token_info["expiration_time"] = time.time() + payload["timeout"]
        print("Token created successfully!")
    except requests.RequestException as e:
        print(f"Error creating token: {e}")
        token_info["token"] = None

def is_token_valid():
    """
    Check if the current token is still valid.
    """
    return token_info["token"] and token_info["expiration_time"] and time.time() < token_info["expiration_time"]

def get_token(mcp):
    """
    Get a valid token, creating a new one if necessary.
    """
    if not is_token_valid():
        create_token(mcp)
    return token_info["token"]

def upload_script(mcp, product_type, protocol_type, script_name, description, file_path):
    """
    Upload a custom script to Navigator.
    """
    url = f"https://{mcp}/configmgmt/api/v1/customScripts"
    token = get_token(mcp)
    headers = {
        "Authorization": f"Bearer {token}",
        "Accept": "application/json"
    }

    if not os.path.exists(file_path):
        print(f"File not found: {file_path}")
        return

    data = {
        "typeGroup": product_type,
        "protocolType": protocol_type,
        "scriptName": script_name,
        "description": description
    }

    try:
        with open(file_path, "rb") as file:
            files = {
                "file": (os.path.basename(file_path), file, "text/plain")
            }
            response = requests.post(url, headers=headers, data=data, files=files, verify=False)
            response.raise_for_status()
            print(f"Custom Script '{script_name}' uploaded successfully!")
    except requests.RequestException as e:
        print(f"Error uploading script '{script_name}': {e}")

def process_scripts_file(mcp, scripts_file):
    """
    Process the scripts file and upload each script.
    """
    if not os.path.exists(scripts_file):
        print(f"Scripts file not found: {scripts_file}")
        return

    try:
        with open(scripts_file, 'r') as scripts:
            for line in scripts:
                parsed_line = line.strip().split(',')
                if len(parsed_line) < 4:
                    print(f"Invalid line format: {line}")
                    continue

                script_name = parsed_line[0].strip()
                product_type = parsed_line[1].strip()
                protocol_type = parsed_line[2].strip()
                file_path = parsed_line[3].strip()
                description = parsed_line[4].strip() if len(parsed_line) > 4 else ""

                upload_script(mcp, product_type, protocol_type, script_name, description, file_path)
                time.sleep(2)  # Optional delay between uploads
    except Exception as e:
        print(f"Error processing scripts file: {e}")

def main():
    """
    Main function to process command-line arguments and initiate script uploads.
    """
    if len(sys.argv) < 3:
        print("Usage: uploadCustomScripts.py <Navigator-IP-Address> <FileWithInfoOnScriptsToBeUploaded>")
        print("Each line in the file should be:")
        print("ScriptName,productTypeGroup,protocolType,fileWithDirectoryStructure")
        return

    mcp_ip = sys.argv[1]
    scripts_file = sys.argv[2]

    process_scripts_file(mcp_ip, scripts_file)

if __name__ == "__main__":
    main()