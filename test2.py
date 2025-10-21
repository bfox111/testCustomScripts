import unittest
import importlib.util
import os
import json
import subprocess

class DeviceTestFramework(unittest.TestCase):
    def setUp(self):
        """Setup code before each test case."""
        self.script_directory = "uploaded_scripts"  # Directory containing external scripts
        self.script_order_file = "test_plan.json"  # File containing test plan
        self.scripts = self.load_scripts()
        self.test_plan = self.load_test_plan()

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

    def load_test_plan(self):
        """Load test plan from JSON file."""
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
        for step in self.test_plan:
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