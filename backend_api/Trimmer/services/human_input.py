"""
human_input.py

Handles human-in-the-loop (HITL) interruptions for the Trimmer workflow.
This service throws an exception to pause graph execution and signals the
Streamlit UI to collect manual input.
"""

import re
from typing import List, Union


class HumanInputRequired(Exception):
    """
    Custom exception raised when a LangGraph node needs manual user input.

    Attributes:
        request (dict): A payload containing the 'prompt', 'key', and 'default'
                        values needed by the Streamlit UI to render the input form.
    """

    def __init__(self, request: dict):
        super().__init__("Human input required to proceed.")
        self.request = request


def require_human_input(state: dict, prompt: str, key: str, default: str = "1"):
    """
    Checks if the requested input already exists in the workflow state.
    If not, it interrupts the workflow by raising HumanInputRequired.

    Args:
        state (dict): The current LangGraph state, which must include 'ui_inputs'.
        prompt (str): The text or numbered menu options to display to the user.
        key (str): The unique dictionary key used to store/retrieve this specific input.
        default (str): The default value to display in the Streamlit input box.

    Returns:
        The value provided by the user (int, float, or str depending on the UI parsing).

    Raises:
        HumanInputRequired: If the key is not found in state['ui_inputs'].
    """
    # 1. Check if the Streamlit UI has already injected the answer into the state
    ui_inputs = state.get("ui_inputs", {})

    if key in ui_inputs:
        return ui_inputs[key]

    # 2. If no answer is found, package the request for the Streamlit frontend
    request_payload = {
        "prompt": prompt,
        "key": key,
        "default": default
    }

    # 3. Raise the exception. The thread worker in app.py will catch this,
    # push it to the queue, and safely terminate the current thread.
    raise HumanInputRequired(request_payload)


def parse_prompt_options(prompt: str) -> List[str]:
    """Extract numbered menu options from a trimmer prompt."""
    return re.findall(r"^\s*\d+\)\s*(.+)$", (prompt or "").strip(), re.MULTILINE)


def normalize_human_answer(prompt: str, answer: str) -> Union[int, float]:
    """Convert a UI answer into the value stored in trimmer ui_inputs."""
    options = parse_prompt_options(prompt)
    if options:
        return options.index(answer) + 1
    return float(answer)