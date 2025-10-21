import json

# Select the device and script
device_name = "PE-6x"
script_name = "cliCutThrough"
cmd_file = "ShutOffInactivityTimer"
script_attributes = {
    "NTP_SERVER": "10.92.44.130",
    "HOSTNAME": device_name,
    "MCP_IP_ADDRESS": "10.92.44.121"
}

# Build the payload
payload = {
    "operation": "run",
    "scripts": [
        {
            "scriptName": script_name,
            "inputs": [
                {
                    "cmdFile": cmd_file,
                    "scriptAttributes": script_attributes,
                    "protocolType": "cli"
                }
            ]
        }
    ],
    "included": [
        {
            "id": device_name,
            "type": "connectionAttributes",
            "attributes": data["devices"][device_name]["attributes"]
        }
    ]
}

# Print the payload
print(json.dumps(payload, indent=4))