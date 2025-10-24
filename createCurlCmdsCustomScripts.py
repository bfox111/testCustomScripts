#!/usr/bin/env python

"""
Author: Barbara A. Fox <bfox@ciena.com>

Create CURL commands to Upload custom scripts to a particular Navigator.

Lots of help from Harry Solomou  And ChatGPT!
"""

import sys
import requests
import time
import os

mcp = "10.92.44.121"
# mcp = "10.75.1.239"
# custom_scripts_file = "/mnt/c/Users/bfox/OneDrive - Ciena Corporation/Documents/Customers/Lightpath/NCS-Customize/uploadCustomScripts.txt"
custom_scripts_file = "/mnt/c/Users/bfox/OneDrive - Ciena Corporation/Documents/Customers/Lightpath/NCS-Customize/LPCustomScripts.csv"
curl_file = "/mnt/c/Users/bfox/OneDrive - Ciena Corporation/Documents/Customers/Lightpath/NCS-Customize/curl_commands.txt"

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

        
        
def main():
    """
    Main function to process scripts file and upload each script.
    """

    if (len(sys.argv) < 3): 
        print("uploadCustomScripts <Navigator-IP-Address> <FileWithInfoOnScriptsToBeUploaded>")   
        print("Each line in the file should be: ")   
        print("ScriptName,productTypeGroup,protocolType,fileWithDirectoryStructure")
        print("Usage:  uploadCustomScripts.py <NCS-IP-Addr> <file-with-custom-script-info>")

    if len(sys.argv) >1:
        mcp_ip = sys.argv[1]
    else:
        mcp_ip = mcp
        print("You need to specify the MCP/Navigator IP address")
        print("Usage:  uploadCustomScripts.py <NCS-IP-Addr> <file-with-custom-script-info>")


    if len(sys.argv) >2:
        scripts_file = sys.argv[2]
    else:
        scripts_file = custom_scripts_file

    try:
        if not os.path.exists(scripts_file):
            print(f"Scripts file not found: {scripts_file}")
            return

        curl_cmds = open(curl_file, 'w')
        bearer_token = get_token(mcp_ip)

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

                curl_line = f"curl -X POST https://{mcp_ip}/configmgmt/api/v1/customScripts -H 'accept: application/json' -H 'Authorization: Bearer {bearer_token}' -H 'Content-Type: multipart/form-data' -F 'typeGroup={productType}' -F 'protocolType={protocolType}' -F 'scriptName={name}' -F 'description={description}' -F 'file=@{file_path};type=text/plain' -k"

                curl_cmds.write(curl_line + "\n")

    except Exception as e:
        print(f"Error processing scripts file: {e}")
        
    curl_cmds.close()


if __name__ == "__main__":
    main()



