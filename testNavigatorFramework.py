import unittest
import requests
import jsonunit
import time

class NavigatorTestFramework(unittest.TestCase):
    def setUp(self):
        """Setup code before each test case."""
        self.navigator_base_url = "https://10.75.1.243"  # Replace with Navigator IP or base URL
        self.auth_url = f"{self.navigator_base_url}/tron/api/v2/tokens"  # Endpoint to get the token
        self.script_execution_url = f"{self.navigator_base_url}/configmgmt/api/v1/customScripts/execute"  # Endpoint for script execution
        self.auth_payload = {
            "username": "admin",  # Replace with your username
            "password": "adminpw",  # Replace with your password
            "timeout": 3600  # Token expiration in seconds
        }
        self.token_info = {"token": None, "expiration_time": None}
        self.script_order_file = "test_plan.json"  # File containing test plan

        # Load test plan
        self.test_plan = self.load_test_plan()

    def create_token(self):
        """Create a new token for authentication."""
        response = requests.post(self.auth_url, json=self.auth_payload, verify=False)
        if response.status_code == 201:
            token_data = response.json()
            self.token_info["token"] = token_data.get("token")
            self.token_info["expiration_time"] = time.time() + self.auth_payload["timeout"]
            print("Token created successfully!")
        else:
            print(f"Failed to create token: {response.status_code}, {response.text}")
        """Create a new token for Navigator."""
        try:
            response = requests.post(self.auth_url, data=self.auth_payload, headers={"Content-Type": "application/x-www-form-urlencoded"}, verify=False)
            if response.status_code == 201:
                token_data = response.json()
                self.token_info["token"] = token_data.get("token")
                self.token_info["expiration_time"] = time.time() + self.auth_payload["timeout"]
                print("Token created successfully!")
            else:
                self.fail(f"Failed to create token: {response.status_code}, {response.text}")
        except requests.RequestException as e:
            self.fail(f"Error creating token: {e}")

    def is_token_valid(self):
        """Check if the token is still valid."""
        if self.token_info["token"] and self.token_info["expiration_time"]:
            return time.time() < self.token_info["expiration_time"]
        return False

    def get_token(self):
        """Get a valid token, creating one if necessary."""
        if self.is_token_valid():
           return self.token_info["token"]
        self.create_token()
        return self.token_info["token"]

    def load_test_plan(self):
        """Load test plan from JSON file."""
        if not os.path.exists(self.script_order_file):
            raise FileNotFoundError(f"{self.script_order_file} not found.")
        with open(self.script_order_file, "r") as file:
            return json.load(file)

    def execute_script_in_navigator(self, script_name, params):
        """Execute a script directly in Navigator."""
        token = self.get_token()
        headers = {"Authorization": f"Bearer {token}", "accept": "application/json"}
        payload = {
            "scriptName": script_name,
            "parameters": params
        }

        try:
            response = requests.post(self.script_execution_url, headers=headers, json=payload, verify=False)
            if response.status_code == 200:
                execution_result = response.json()
                print(f"Script '{script_name}' executed successfully.")
                print(f"Execution Output: {execution_result}")
                return execution_result
            else:
                self.fail(f"Failed to execute script '{script_name}' in Navigator. Status code: {response.status_code}, {response.text}")
        except requests.RequestException as e:
            self.fail(f"Error executing script '{script_name}' in Navigator: {e}")

    def validate_cfm_delay(self, output):
        """Validate CFM delay calculation."""
        # Custom parsing logic for CFM delay
        if "CFM delay" in output:
            print("CFM delay validated successfully.")
            return True
        else:
            print("CFM delay validation failed.")
            return False

    def validate_sat_test(self, output):
        """Validate SAT test results."""
        # Custom parsing logic for SAT test
        if "SAT test passed" in output:
            print("SAT test validated successfully.")
            return True
        else:
            print("SAT test validation failed.")
            return False

    def test_execute_scripts_and_validate(self):
        """Execute scripts in Navigator, validate output, and handle pass/fail logic."""
        for step in self.test_plan:
            script_name = step["script"]
            params = step.get("params", {})
            validation_type = step.get("validation_type", None)

            # Execute the script in Navigator
            execution_result = self.execute_script_in_navigator(script_name, params)

            # Validate based on test type
            if validation_type == "cfm_delay":
                valid = self.validate_cfm_delay(execution_result.get("output", ""))
            elif validation_type == "sat_test":
                valid = self.validate_sat_test(execution_result.get("output", ""))
            else:
                self.fail(f"Unknown validation type: {validation_type}")

            self.assertTrue(valid, f"Validation failed for script {script_name}.")

            # Tear down or debug based on result
            if not valid:
                print("Debugging setup due to failure...")
                break  # Stop execution for debugging
            else:
                print("Tearing down setup...")
                # Add teardown logic here

    def tearDown(self):
        """Cleanup code after each test case."""
        self.test_plan = None


if __name__ == "__main__":
    print("Provide a 'test_plan.json' file with test plan details.")
    unittest.main()        
            