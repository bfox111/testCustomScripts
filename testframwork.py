import unittest
import importlib.util
import os
import json
import subprocess

class DeviceConfigurationTestFramework(unittest.TestCase):
    def setUp(self):
        """Setup code before each test case."""
        self.script_directory = "uploaded_scripts"  # Directory containing external scripts
        self.script_order_file = "script_order.json"  # File containing execution order and parameters
        self.scripts = self.load_scripts()
        self.execution_order = self.load_execution_order()

    def load_scripts(self):
        """Load external Python scripts dynamically."""
        scripts = {}
        for filename in os.listdir(self.script_directory):
            if filename.endswith(".py"):
                script_path = os.path.join(self.script_directory, filename)
                module_name = os.path.splitext(filename)[0]
                spec = importlib.util.spec_from_file_location(module_name, script_path)
                module = importlib.util.module_from_spec(spec)
                spec.loader.exec_module(module)
                scripts[module_name] = module
        return scripts

    def load_execution_order(self):
        """Load script execution order and parameters from JSON file."""
        if not os.path.exists(self.script_order_file):
            raise FileNotFoundError(f"{self.script_order_file} not found.")
        with open(self.script_order_file, "r") as file:
            return json.load(file)

    def execute_script(self, script_name, params):
        """Execute a script with given parameters."""
        if script_name in self.scripts:
            script = self.scripts[script_name]
            if hasattr(script, "run_test"):
                result = script.run_test(**params)  # Pass parameters to the script's `run_test` function
                return result
            else:
                self.fail(f"Script {script_name} does not have a 'run_test' function.")
        else:
            self.fail(f"Script {script_name} not found.")

     def query_device(self, command):
        """Query the device and parse the output."""
        try:
            output = subprocess.check_output(command, shell=True, text=True)
            print(f"Command Output: {output}")
            # Add custom parsing logic as needed
            return output
        except subprocess.CalledProcessError as e:
            self.fail(f"Device query failed: {e}")

    def test_execute_scripts_and_verify(self):
        """Execute scripts in order and verify configuration."""
        for step in self.execution_order:
            script_name = step["script"]
            params = step.get("params", {})
            command = step.get("verify_command", None)

            # Execute the script
            result = self.execute_script(script_name, params)
            self.assertTrue(result, f"Script {script_name} execution failed.")

            # Query device for verification
            if command:
                output = self.query_device(command)
                self.assertIn(step["expected_output"], output, f"Verification failed for script {script_name}.")
 
 
 
    def tearDown(self):
        """Cleanup code after each test case."""
        self.scripts = None
        self.execution_order = None


if __name__ == "__main__":
    # Ensure the script directory exists
    if not os.path.exists("uploaded_scripts"):
        os.mkdir("uploaded_scripts")
    print("Place your scripts in the 'uploaded_scripts' directory.")
    print("Provide a 'script_order.json' file with execution order and parameters.")
    unittest.main()
    
 
 
import requests

# Navigator API URL and Authentication
BASE_URL = "https://navigator-api-url"
API_ENDPOINT = "/configmgmt/api/v1/customScripts/execute"
API_URL = f"{BASE_URL}{API_ENDPOINT}"
AUTH_TOKEN = "your_auth_token"  # Replace with your authentication token

# Script Execution Payload
payload = {
    "operation": "run",  # "run" or "saveAndRun"
    "networkElementDetails": [
        {
            "neId": "device_id_1",  # Replace with the device ID
            "neType": "device_type"  # Replace with the device type
        }
    ],
    "scriptDetails": {
        "scriptId": "custom_script_id",  # Replace with the script ID
        "scriptName": "custom_script_name"  # Replace with the script name
    },
    "inputs": {
        "param1": "value1",  # Replace with parameter name and value
        "param2": "value2"   # Replace with parameter name and value
    }
    }

# HTTP Headers
headers = {
    "Authorization": f"Bearer {AUTH_TOKEN}",
    "Content-Type": "application/json"
}

# Execute the Script
response = requests.post(API_URL, json=payload, headers=headers)

# Check the Response
if response.status_code == 200:
    print("Script executed successfully!")
    print("Response:", response.json())
else:
    print("Failed to execute script.")
    print("Error:", response.text)
    