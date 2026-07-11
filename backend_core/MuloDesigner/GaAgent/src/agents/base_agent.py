import os
import re
import json
import time
from typing import Dict, Any

from langchain_openai import ChatOpenAI
from langchain_groq import ChatGroq
from langchain_core.messages import AIMessage

from backend_core.MuloDesigner.GaAgent.src.logger import get_logger

from dotenv import load_dotenv
load_dotenv()

logger = get_logger(__name__)

# Set API keys
os.environ["OPENAI_API_KEY"] = os.getenv("OPENAI_API_KEY")
os.environ["GROQ_API_KEY"] = os.getenv("GROQ_API_KEY")


def extract_json_from_response(response_text: str) -> Dict[str, Any]:
    if not response_text:
        raise json.JSONDecodeError("Empty response", "", 0)
    # Remove thinking tags and their content
    response_text = re.sub(r'<think>.*?</think>', '', response_text, flags=re.DOTALL)
    # Try to find JSON within markdown code blocks
    json_pattern = r'```json\s*\n?(.*?)\n?```'
    json_match = re.search(json_pattern, response_text, re.DOTALL)
    if json_match:
        json_text = json_match.group(1).strip()
    else:
        # Try to find JSON without markdown formatting
        # Look for content that starts with { and ends with }
        brace_pattern = r'\{.*\}'
        brace_match = re.search(brace_pattern, response_text, re.DOTALL)
        if brace_match:
            json_text = brace_match.group(0).strip()
        else:
            # Last resort: use the entire cleaned response
            json_text = response_text.strip()
    try:
        return json.loads(json_text)
    except json.JSONDecodeError as e:
        # Log the problematic text for debugging
        logger.error(f"Failed to parse JSON. Original response: {repr(response_text)}")
        logger.error(f"Extracted JSON text: {repr(json_text)}")
        raise e


def round_floats(obj, decimals=4):
    """Recursively round float values in a nested structure (dict/list) to specified decimals."""
    if isinstance(obj, float):
        return round(obj, decimals)
    elif isinstance(obj, dict):
        return {k: round_floats(v, decimals) for k, v in obj.items()}
    elif isinstance(obj, list):
        return [round_floats(item, decimals) for item in obj]
    return obj


class LLMBaseAgent:
    """Base class for all LLM agents in the control system"""
    def __init__(self, model="deepseek-r1-distill-llama-70b", temperature=0.0, seed=42, monitor=None):
        self.model = model
        self.llm = self._initialize_llm_client(model, temperature, seed)
        self.agent_name = self.__class__.__name__
        self.monitor = monitor

    PRICE_TABLE = {
        "gpt-4o": {"in": 3.0, "out": 10.0},
        "gpt-4o-mini": {"in": 0.15, "out": 0.60},
        "llama3.1-8b": {"in": 0.05, "out": 0.08},
        "llama-3.3-70b": {"in": 0.50, "out": 0.64},
        "llama-3.1-8b-instant": {"in": 0.55, "out": 0.65},
        "qwen-3-32b": {"in": 0.40, "out": 0.80},
        "gpt-oss-120b": {"in": 0.25, "out": 0.69},
        "gpt-oss-20b": {"in": 0.2, "out": 0.3},
        "deepseek-r1-distill-llama-70b": {"in": 0.23, "out": 0.69},
        "llama-3.1-70b": {"in": 0.59, "out": 0.79},
        "qwen-3-max": {"in": 1.20, "out": 6.00},
        "llama-4-maverick": {"in": 0.50, "out": 0.64},
        "llama-3": {"in": 0.50, "out": 0.64},
        "llama3": {"in": 0.50, "out": 0.64},
        "llama-4": {"in": 0.60, "out": 0.80},
        "llama4": {"in": 0.60, "out": 0.80},
        "mistral-nemotron": {"in": 0.04, "out": 0.17},
        "llama-3.3-70b-versatile": {"in": 0.59, "out": 0.79},
        "kimi-k2-instruct": {"in": 1.00, "out": 3.00},
    }

    def _initialize_llm_client(self, model, temperature, seed):
        """Initialize the appropriate LLM client based on the model name"""
        # OpenAI models
        openai_models = [
            "gpt-3.5-turbo", "gpt-3.5-turbo-0125", "gpt-3.5-turbo-1106",
            "gpt-4", "gpt-4-turbo", "gpt-4-turbo-preview", "gpt-4-0125-preview",
            "gpt-4o", "gpt-4o-mini", "o1-preview", "o1-mini"
        ]
        # Groq models
        groq_models = [
            "groq/compound",
            "groq/compound-mini",
            "llama-3.1-8b-instant",
            "llama-3.3-70b-versatile",
            "meta-llama/llama-4-maverick-17b-128e-instruct",
            "meta-llama/llama-4-scout-17b-16e-instruct",
            "meta-llama/llama-guard-4-12b",
            "meta-llama/llama-prompt-guard-2-22m",
            "meta-llama/llama-prompt-guard-2-86m",
            "moonshotai/kimi-k2-instruct",
            "moonshotai/kimi-k2-instruct-0905",
            "openai/gpt-oss-120b",
            "openai/gpt-oss-20b",
            "openai/gpt-oss-safeguard-20b",
            "playai-tts",
            "playai-tts-arabic",
            "qwen/qwen3-32b",
            "whisper-large-v3",
            "whisper-large-v3-turbo"
        ]

        if any(openai_model in model for openai_model in openai_models):
            return ChatOpenAI(
                model=model,
                temperature=temperature,
                seed=seed,
                api_key=os.getenv("OPENAI_API_KEY"),
                model_kwargs={
                    "response_format": {"type": "json_object"} if "gpt-" in model else {}
                }
            )
        elif any(groq_model in model for groq_model in groq_models):
            return ChatGroq(
                model=model,
                temperature=temperature,
                api_key=os.getenv("GROQ_API_KEY"),
                model_kwargs={"seed": seed}
            )

        else:
            # Default fallback
            print(f"Warning: Unknown model '{model}', defaulting to Groq client")
            return ChatGroq(
                model=model,
                temperature=temperature,
                api_key=os.getenv("GROQ_API_KEY"),
                model_kwargs={"seed": seed}
            )

    def invoke_llm(self, system_prompt, user_prompt, max_retries=3):
        """Invoke LLM with separate system and user prompts, retry logic and logging"""
        for attempt in range(max_retries):
            try:
                if attempt > 0:
                    logger.info(f"Retry attempt {attempt + 1}/{max_retries} for {self.agent_name}")
                messages = [
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": user_prompt}
                ]
                llm_start_time = time.time()
                response = self.llm.invoke(messages)
                llm_duration = time.time() - llm_start_time

                if isinstance(response, AIMessage):
                    response_text = response.content
                    if hasattr(response, 'usage_metadata') and response.usage_metadata:
                        usage = {
                            'prompt_tokens': response.usage_metadata.get('input_tokens', 0),
                            'completion_tokens': response.usage_metadata.get('output_tokens', 0)
                        }
                    elif hasattr(response, 'response_metadata') and response.response_metadata:
                        usage_data = response.response_metadata.get('usage', {})
                        usage = {
                            'prompt_tokens': usage_data.get('prompt_tokens', 0),
                            'completion_tokens': usage_data.get('completion_tokens', 0)
                        }
                    else:
                        usage = {'prompt_tokens': 0, 'completion_tokens': 0}
                else:
                    response_text = str(response)
                    usage = {'prompt_tokens': 0, 'completion_tokens': 0}

                usage['llm_time'] = llm_duration

                if self.monitor:
                    full_prompt = f"System: {system_prompt}\n\nUser: {user_prompt}"
                    truncated_prompt = full_prompt[:200] + "..." if len(full_prompt) > 200 else full_prompt
                    self.monitor.add_llm_response(self.agent_name, truncated_prompt, response_text)

                return response_text, usage
            except Exception as e:
                overhead_time = 0.01
                logger.error(
                    f"Error invoking LLM (attempt {attempt + 1}/{max_retries}): {type(e).__name__}: {e}"
                )
                if attempt == max_retries - 1:
                    raise e
        return None, {'prompt_tokens': 0, 'completion_tokens': 0, 'llm_time': 0.0}

    def _compute_cost(self, in_tokens: int, out_tokens: int) -> float:
        """Compute cost based on model and tokens (price_table in $/1M tokens)"""

        model_name = getattr(self, "model", "unknown").lower()
        if "/" in model_name:
            model_name = model_name.split("/", 1)[1]

        if model_name in self.PRICE_TABLE:
            prices = self.PRICE_TABLE[model_name]
            cost = (prices["in"] * in_tokens + prices["out"] * out_tokens) / 1_000_000
            return cost

        llama_match = re.match(r'(llama-?\d+(?:\.\d+)?)', model_name)
        if llama_match:
            base_model = llama_match.group(1)
            if base_model in self.PRICE_TABLE:
                prices = self.PRICE_TABLE[base_model]
                cost = (prices["in"] * in_tokens + prices["out"] * out_tokens) / 1_000_000
                logger.info(f"Using base model '{base_model}' pricing for '{self.model}'")
                return cost

        if "maverick" in model_name:
            maverick_match = re.match(r'(llama-\d+-maverick)', model_name)
            if maverick_match:
                base_model = maverick_match.group(1)
                if base_model in self.PRICE_TABLE:
                    prices = self.PRICE_TABLE[base_model]
                    cost = (prices["in"] * in_tokens + prices["out"] * out_tokens) / 1_000_000
                    logger.info(f"Using maverick model '{base_model}' pricing for '{self.model}'")
                    return cost

        return 0.0
