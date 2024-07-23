import os
import logging
from typing import Annotated
import subprocess
from langchain_core.tools import tool
from dotenv import load_dotenv
from logger import setup_logger
# Load environment variables
load_dotenv()
# Initialize logger
logger = setup_logger()

# Get storage path from environment variable
storage_path = os.getenv('STORAGE_PATH', './data_storage/')

# Ensure the storage directory exists
if not os.path.exists(storage_path):
    os.makedirs(storage_path)
    logger.info(f"Created storage directory: {storage_path}")

@tool
def execute_code(
    input_code: Annotated[str, "The Python code to execute to generate your chart."],
    codefile_name: Annotated[str, "The Python code file name."]
):
    """
    Execute Python code and return the result.

    This function takes Python code as input, writes it to a file, executes it,
    and returns the output or any errors encountered during execution.

    Args:
    input_code (str): The Python code to be executed.
    codefile_name (str): The name of the file to save the code in.

    Returns:
    dict: A dictionary containing the execution result, output, and file path.
    """
    try:
        # Define the path for the code file
        code_file_path = os.path.join(storage_path, f'{codefile_name}')
        
        # Write the input code to the file
        with open(code_file_path, 'w') as code_file:
            code_file.write(input_code)
        
        logger.info(f"Code written to file: {code_file_path}")
        
        # Execute the code using subprocess for security
        result = subprocess.run(['python', code_file_path], capture_output=True, text=True)
        
        # Capture standard output and error output
        output = result.stdout
        error_output = result.stderr
        
        if result.returncode == 0:
            logger.info("Code executed successfully")
            print(output)
            return {
                "result": "Code executed successfully",
                "output": output + "\n\nIf you have completed all tasks, respond with FINAL ANSWER.",
                "file_path": code_file_path
            }
        else:
            logger.error(f"Code execution failed: {error_output}")
            print(error_output)
            return {
                "result": "Failed to execute",
                "error": error_output,
                "file_path": code_file_path
            }
    except Exception as e:
        logger.exception("An error occurred while executing code")
        return {
            "result": "Error occurred",
            "error": str(e),
            "file_path": code_file_path
        }

@tool
def execute_command(
    command: Annotated[str, "Command to be executed."]
) -> Annotated[str, "Output of the command."]:
    """
    Execute a command in a specified Conda environment and return its output.

    This function activates a Conda environment named 'dcbot', executes the given command,
    and returns the output or any errors encountered during execution.

    Args:
    command (str): The command to be executed in the Conda environment.

    Returns:
    str: The output of the command or an error message.
    """
    try:
        # Get Conda-related paths from environment variables
        conda_path = os.getenv('CONDA_PATH', '/home/e806/anaconda3')
        conda_env = os.getenv('CONDA_ENV', 'dcbot')

        # Construct the command to activate the Conda environment and execute the given command
        source = f"source {conda_path}/etc/profile.d/conda.sh"
        conda_activate = f"conda activate {conda_env}"
        full_command = f"{source} && {conda_activate} && {command}"
        
        logger.info(f"Executing command: {command}")
        
        # Execute the command and capture the output
        result = subprocess.run(
            full_command,
            shell=True,
            check=True,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True,
            executable="/bin/bash"
        )
        logger.info("Command executed successfully")
        return result.stdout
    except subprocess.CalledProcessError as e:
        logger.error(f"Error executing command: {e.stderr}")
        return f"Error: {e.stderr}"

logger.info("Module initialized successfully")