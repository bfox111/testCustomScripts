# getDevices.py

#   Creates a devices structure from a CSV file.
#   The CSV file has a line for each device with the following format:
#
#        device_name,ip_address,ne_product_type,<6x|10x>
    

import csv
import os
from executeCliCommands import execute_cli_commands

from netmiko import ConnectHandler

credentials = {}

def get_shared_mac(devices, router, credentials):

    try:
        type_group = devices[router]["attributes"]["typeGroup"]
        user = credentials[type_group]["user"]
        user_pw = credentials[type_group]["user_pw"]

        if type_group == "PN6x":
            cmd = "chassis show mac"
            mac_name = "Benchmark"
        else:
            cmd = "show system mac"
            mac_name = "shared-mac"
    except KeyError:
        print(f"Error: Device '{router}' or its attributes are missing.")


    # Connect to the device
    connection = ConnectHandler(
        device_type="ciena_saos",  # Adjust device type if necessary
        host=devices[router]["ipAddress"],
        username=user,
        password=user_pw
    )

    # Execute the command

    output = connection.send_command(cmd)
    connection.disconnect()

    # Parse the output
    shared_mac = None
    lines = output.splitlines()
    for line in lines:
        if mac_name in line:
            # Extract the MAC address from the line
            parts = line.split("|")
            if len(parts) > 2:
                shared_mac = parts[2].strip()  # Base MAC is the third column
                print(f"Device '{router}' mac addr is '{shared_mac}'")
            break

    return shared_mac

def create_devices_structure(csv_file, credentials):
    devices = {}

    # Check if the file exists
    if not os.path.exists(csv_file):
        print(f"Error: File '{csv_file}' does not exist.")
        return devices

    try:
        # Open the CSV file and read its contents
        with open(csv_file, mode="r") as file:
            csv_reader = csv.reader(file)

            # Iterate through each row in the CSV file
            for row in csv_reader:
                # Validate the row format (should have exactly 4 columns)
                if len(row) != 4:
                    print(f"Error: Invalid row format: {row}")
                    continue

                device_name, ip_address, ne_type, type_group = row

                # Add the device information to the devices structure
                devices[device_name] = {
                    "attributes": {
                        "neName": device_name,
                        "neType": ne_type,
                        "typeGroup": f"PN{type_group}"  # Prefix typeGroup with "PN"
                    },
                    "ipAddress": ip_address,
                    "macAddress": None  # Placeholder for MAC address if not provided
                }

    except Exception as e:
        print(f"Error: An error occurred while processing the file: {e}")
        
    for router in devices:
        # Get the shared MAC address for each device
        shared_mac = get_shared_mac(devices, router, credentials)
        if shared_mac:
            devices[router]["macAddress"] = shared_mac
        else:
            print(f"Error: Could not retrieve MAC address for device '{router}'.")

    return devices

def create_credentials(csv_file):

    # Check if the file exists
    if not os.path.exists(csv_file):
        print(f"Error: File '{csv_file}' does not exist.")
        return credentials
    
    try:
        # Open the CSV file and read its contents
        with open(csv_file, mode="r") as file:
            csv_reader = csv.reader(file)

            # Iterate through each row in the CSV file
            for row in csv_reader:
                # Validate the row format (should have exactly 4 columns)
                if len(row) != 3:
                    print(f"Error: Invalid row format: {row}")
                    continue

                type_group, user, user_pw = row

                # Add the device information to the devices structure
                credentials[type_group] = {
                    "user": user,
                    "user_pw": user_pw  # Placeholder for MAC address if not provided
                }

    except Exception as e:
        print(f"Error: An error occurred while processing the file: {e}")

    return credentials
