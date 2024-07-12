import sys
from typing import Dict, List, Any

import requests
import anthropic

sys.path.append('libs')
from env_manager import EnvironmentLoader, ANSIColors

# Constants for file paths and story types
PROMPTS_PATH = "./prompts/"
STORY_TYPE_STARTED = "started"
STORY_TYPE_UNSTARTED = "unstarted"
STORY_TYPE_DEFAULT = "default"


class Main:
    def __init__(self):
        # Initialize environment variables and AI client
        env_loader = EnvironmentLoader()
        env_vars = env_loader.get_env_vars()
        if not all(env_vars.values()):
            sys.exit(1)
        
        # Set up instance variables from environment
        self.ai_api_key = env_vars['AI_API_KEY']
        self.ai_model = env_vars['AI_MODEL']
        self.ai_temperature = float(env_vars['AI_TEMPERATURE'])
        self.ai_max_tokens = int(env_vars['AI_MAX_TOKENS'])
        self.pivotal_token = env_vars['PIVOTAL_TOKEN']
        self.pivotal_project_id = env_vars['PIVOTAL_PROJECT_ID']
        
        # Initialize Anthropic client
        self.client = anthropic.Anthropic(api_key=self.ai_api_key)

    def call_ai(self, system_prompt: str, messages: List[Dict[str, Any]]) -> str:
        """
        Call the AI model with the given system prompt and messages.
        
        :param system_prompt: The system prompt to provide context to the AI
        :param messages: List of message dictionaries to send to the AI
        :return: The AI's response as a string
        """
        try:
            message = self.client.messages.create(
                model=self.ai_model,
                max_tokens=self.ai_max_tokens,
                temperature=self.ai_temperature,
                system=system_prompt,
                messages=messages
            )        
            return message.content[0].text
        except Exception as e:
            print(f"Error calling AI: {e}")
            return ""

    def get_system_prompt(self, prompt_type: str) -> str:
        """
        Read and return the system prompt from a file.
        
        :param prompt_type: The type of prompt to read
        :return: The content of the prompt file as a string
        """
        try:
            with open(f'{PROMPTS_PATH}{prompt_type}.prompt', 'r') as file:
                return file.read().replace('\n', '\\n')
        except FileNotFoundError:
            print(f"Prompt file not found: {prompt_type}")
            return ""

    def get_pivotal_data(self, stories_type: str) -> List[Dict[str, Any]]:
        """
        Fetch data from Pivotal Tracker API.
        
        :param stories_type: The type of stories to fetch (e.g., 'started', 'unstarted')
        :return: List of dictionaries containing story data
        """
        print(f"{ANSIColors.BLUE}[get_pivotal_data:{stories_type}]{ANSIColors.RESET}")
        try:
            response = requests.get(
                f'https://www.pivotaltracker.com/services/v5/projects/{self.pivotal_project_id}/stories',
                params={'with_state': stories_type},
                headers={'X-TrackerToken': self.pivotal_token}
            )
            response.raise_for_status()
            return response.json()
        except requests.RequestException as e:
            print(f"Error fetching Pivotal data: {e}")
            return []

    def call_default(self, user_input: str) -> str:
        """
        Handle default AI call without Pivotal data.
        
        :param user_input: The user's input string
        :return: The AI's response
        """
        print(f"{ANSIColors.BLUE}[call_default]{ANSIColors.RESET}")
        system_prompt = self.get_system_prompt(STORY_TYPE_DEFAULT)
        messages = [
            {
                "role": "user",
                "content": [{"type": "text", "text": user_input}]
            }
        ]
        response = self.call_ai(system_prompt, messages)
        print(f"{ANSIColors.BLUE}call_default_response:{ANSIColors.RESET}")
        print(f"{ANSIColors.YELLOW}{response}{ANSIColors.RESET}")
        return response

    def call_detail(self, user_input: str, stories_type: str) -> str:
        """
        Handle detailed AI call with Pivotal data.
        
        :param user_input: The user's input string
        :param stories_type: The type of stories to use (e.g., 'started', 'unstarted')
        :return: The AI's response based on Pivotal data
        """
        print(f"{ANSIColors.BLUE}[call_detail]{ANSIColors.RESET}")
        system_prompt = self.get_system_prompt("detail")
        pivotal_data = self.get_pivotal_data(stories_type)
        messages = [
            {"role": "user", "content": [{"type": "text", "text": f"Here is the data you must use to answer my question: {pivotal_data}"}]},
            {"role": "assistant", "content": [{"type": "text", "text": "Understood, I will use this data to answer your questions. What would you like to know?"}]},
            {"role": "user", "content": [{"type": "text", "text": "It is of utmost importance that your answer is based solely on this data!"}]},
            {"role": "assistant", "content": [{"type": "text", "text": "I understand. I will answer your questions strictly based on the provided data. What would you like to know?"}]},
            {"role": "user", "content": [{"type": "text", "text": user_input}]}
        ]
        return self.call_ai(system_prompt, messages)

    def handle_input(self, user_input: str) -> str:
        """
        Handle user input and return appropriate response.
        
        :param user_input: The user's input string
        :return: The final response based on the input and potential Pivotal data
        """
        default_response = self.call_default(user_input)
        
        if default_response == STORY_TYPE_STARTED:
            return self.call_detail(user_input, stories_type=STORY_TYPE_STARTED)
        elif default_response == STORY_TYPE_UNSTARTED:
            return self.call_detail(user_input, stories_type=STORY_TYPE_UNSTARTED)
        else:
            return default_response


def main():
    """
    Main function to handle command-line input and process it through the AI system.
    """
    main_instance = Main()
    if len(sys.argv) > 1:
        response = main_instance.handle_input(sys.argv[1])
        print(f"{ANSIColors.BLUE}AI Final Response:{ANSIColors.RESET}\n{ANSIColors.GREEN}{response}{ANSIColors.RESET}")
    else:
        print("No argument provided\nUse python main.py \"<request>\"")


if __name__ == "__main__":
    main()
