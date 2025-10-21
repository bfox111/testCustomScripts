from netmiko import ConnectHandler

def execute_cli_commands(ip, username, password, cli_commands):
    """
    Executes a list of CLI commands on a device using Netmiko.

    Args:
        ip (str): IP address of the device.
        username (str): Username for authentication.
        password (str): Password for authentication.
        cli_commands (list): List of CLI commands to execute.

    Returns:
        None
    """
    # Remove empty commands from the list
    cli_commands = [command.strip() for command in cli_commands if command.strip()]

    # Connect to the device
    connection = ConnectHandler(device_type='ciena_saos', host=ip, username=username, password=password)
    
# Disable session paging and enter configuration mode
    connection.send_command_timing('set session more off')

    # Execute each command and print the output
    for command in cli_commands:
        print(f"Executing: {command}")
        output = connection.send_command_timing(command)
        print(f"Output:\n{output}")

    # Disconnect from the device
    connection.disconnect()

