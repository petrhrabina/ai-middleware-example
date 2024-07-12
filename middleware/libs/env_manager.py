import os
import sys
from pathlib import Path

from dotenv import load_dotenv


class ANSIColors:
    """
    ANSI color codes for terminal output formatting.
    """
    RESET = "\033[0m"
    RED = "\033[91m"
    GREEN = "\033[92m"
    YELLOW = "\033[93m"
    BLUE = "\033[94m"


class EnvironmentLoader:
    """
    Handles loading and verification of environment variables.
    """
    def __init__(self):
        # List of required environment variables
        self.required_env_vars = [
            "AI_API_KEY",
            "AI_MODEL",
            "AI_TEMPERATURE",
            "AI_MAX_TOKENS",
            "PIVOTAL_TOKEN",
            "PIVOTAL_PROJECT_ID"
        ]
        self.env_vars = {}
        self.load_env()
        self.verify_env()

    def load_env(self):
        """
        Loads environment variables from .env file in the project root directory.
        Exits if required variables are missing.
        """
        project_root = Path(__file__).resolve().parent.parent
        env_path = project_root / '../.env'
        
        if not env_path.exists():
            raise FileNotFoundError(f"{ANSIColors.RED}.env file not found in {env_path}{ANSIColors.RESET}")
        
        load_dotenv(dotenv_path=env_path)
        
        missing_vars = []
        for var in self.required_env_vars:
            value = os.getenv(var)
            self.env_vars[var] = value
            if not value:
                missing_vars.append(var)
        
        if missing_vars:
            print(f"{ANSIColors.RED}Missing environment variables:{ANSIColors.RESET}")
            for var in missing_vars:
                print(f"{ANSIColors.RED}- {var}{ANSIColors.RESET}")
            sys.exit(1)

    def verify_env(self):
        """
        Verifies if all required environment variables are set.
        Raises EnvironmentError if any are missing.
        """
        missing_vars = [var for var in self.required_env_vars if not self.env_vars[var]]
        if missing_vars:
            raise EnvironmentError(f"{ANSIColors.RED}Missing environment variables: {', '.join(missing_vars)}{ANSIColors.RESET}")

    def get_env_vars(self):
        """
        Returns a dictionary with loaded environment variables.
        
        :return: Dictionary of environment variables
        """
        return self.env_vars
