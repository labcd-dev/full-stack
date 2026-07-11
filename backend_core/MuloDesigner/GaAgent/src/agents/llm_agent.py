from typing import Dict, Tuple
from backend_core.MuloDesigner.GaAgent.src.agents.base_agent import LLMBaseAgent
from backend_core.MuloDesigner.GaAgent.src.logger import get_logger

# Get logger for this module
logger = get_logger(__name__)


class LLMAgent(LLMBaseAgent):
    """Legacy wrapper to maintain compatibility with existing code"""
    def __init__(self, model: str = "gpt-4o-mini", temperature: float = 0.0):
        super().__init__(model=model, temperature=temperature)
        self.agent_name = "DesignAgent"

    def invoke(self, system_prompt: str, user_prompt: str) -> Tuple[str, Dict[str, int]]:
        """Compatibility method matching original signature"""
        response_text, usage = self.invoke_llm(system_prompt, user_prompt)
        # Convert usage dict to match old format
        usage_compat = {
            'prompt_tokens': usage.get('prompt_tokens', 0),
            'completion_tokens': usage.get('completion_tokens', 0)
        }
        logger.debug(f"{self.agent_name}: "
              f"Tokens in={usage_compat['prompt_tokens']}, out={usage_compat['completion_tokens']}")
        return response_text, usage_compat
