import json
import time
import sys
from getDevices import create_credentials, create_devices_structure
from executeCliCommands import execute_cli_commands
from executeNCSCustomScript import execute_custom_script

credentials = create_credentials("deviceCredentials.txt")
devices = create_devices_structure("testDevices.txt", credentials)
mcp = "10.92.44.121"
# mcp = "10.75.1.205"
# test_plan_file = "testplan.json"  # Specify the path to your JSON file
test_plan_file = "testplan.json"  # Specify the path to your JSON file

def load_test_plan(file_path):
    """Load the test plan from a JSON file."""
    try:
        with open(file_path, 'r') as file:
            return json.load(file)
    except FileNotFoundError:
        print(f"Error: The file {file_path} was not found.")
        return None
    except json.JSONDecodeError as e:
        print(f"Error: Failed to parse JSON file. {e}")
        return None

def process_test_case(mcp, test_case):
    """Process an individual test case."""
    print("\n=== Test Case ===")
    print("Test Name:", test_case.get("testName", "N/A"))
    print("Description:", test_case.get("testDescription", "N/A"))
    print("Test Type:", test_case.get("testType", "N/A"))

    # Process custom scripts
    custom_scripts = test_case.get("customScripts", [])
    if custom_scripts:
        print("\n--- Custom Scripts ---")
        for script in custom_scripts:
            print(f"Device Name: {script.get('deviceName', 'N/A')}")
            print(f"Command File: {script.get('cmdFile', 'N/A')}")
            cmdFile = script.get("cmdFile", "N/A")
            script_attributes = script.get("scriptAttributes", {})

            if cmdFile.startswith("Y1564Setup") or cmdFile.startswith("RFC2544Setup"):
                script_attributes['DEST_MAC'] = devices[script_attributes['DEST_NODE']]['macAddress']
            print("Script Attributes:")
            execute_custom_script(mcp, script.get("deviceName", "N/A"), script.get("cmdFile", "N/A"), script_attributes, devices)


    # Sleep time
    sleep_time = test_case.get("sleepTime", 0)
    print(f"\nSleep Time: {sleep_time} seconds")
    time.sleep(sleep_time)  # Simulate sleep
    
    # Process verification commands
    verification_commands = test_case.get("verificationCommands", {})
    if verification_commands:
        print("\n--- Verification Commands ---")
        for device, commands in verification_commands.items():
            
            type_group = devices[device]["attributes"]["typeGroup"]
            user = credentials[type_group]["user"]
            user_pw = credentials[type_group]["user_pw"]
            host = devices[device]["ipAddress"]

            print(f"Device: {device}")
#            for command in commands:

            print(f"  Commands: {commands}")
            execute_cli_commands(host, user, user_pw, commands)


    
def execute_test_cases(mcp, test_cases):
    """Execute all test cases."""
    print("\n=== Executing Test Cases ===")
    for idx, test_case in enumerate(test_cases, start=1):
        print(f"\n--- Executing Test Case {idx} ---")
        process_test_case(mcp, test_case)

def main():
    """Main function to execute the test plan."""
    if (len(sys.argv) < 3): 
        print("executeTestPlan.py <Navigator-IP-Address> <TestPlanJsonFile>")   
        print("Devices to be tested should be in testDevices.txt in the format: ")   
        print("NE-NAME, IP Address, Device Type, 6x or 10x for example:  PE-6x,10.92.44.44,3928,6x")
        print("Usage:   python 3.10 executeTestPlan.py <Navigator-IP-Address> <TestPlanJsonFile>")

    if len(sys.argv) >1:
        mcp = sys.argv[1]

    if len(sys.argv) >2:
        test_plan_file = sys.argv[2]

    print(devices)
    test_plan = load_test_plan(test_plan_file)
    if test_plan:
        test_cases = test_plan.get("tests", [])
        execute_test_cases(mcp, test_cases)

if __name__ == "__main__":
    main()