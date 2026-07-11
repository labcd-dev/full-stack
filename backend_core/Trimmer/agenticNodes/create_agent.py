import yaml
import os
import json
from typing import Dict, Any, Callable, Optional
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.output_parsers import JsonOutputParser

def make_serializable(obj):
    if callable(obj):
        return str(obj)
    elif hasattr(obj, 'tolist'):
        return obj.tolist()
    elif isinstance(obj, dict):
        return {k: make_serializable(v) for k, v in obj.items()}
    elif isinstance(obj, list):
        return [make_serializable(item) for item in obj]
    else:
        try:
            json.dumps(obj)
            return obj
        except TypeError:
            return str(obj)

def create_agent(llm, template_name: str, state_keys: Optional[Dict[str, str]] = None) -> Callable:
    # Load the YAML configuration
    config = _load_template(template_name)

    # Build the prompt template
    prompt_template = _build_prompt_template(config)

    # Create the chain
    chain = _build_chain(llm, prompt_template, config)

    # Create the node function
    def agent_node(state):
        """LangGraph node function that processes state and returns updated state."""
        # Extract inputs from state based on config
        inputs = _extract_inputs(state, config)

        # Run the chain
        result = chain.invoke(inputs)

        # Process and update state
        updated_state = _update_state(state, result, config)

        return updated_state

    return agent_node

def _load_template(template_name: str) -> Dict[str, Any]:
    """Load YAML template configuration."""
    templates_dir = "backend_core/Trimmer/agenticNodes/templates"
    template_path = os.path.join(templates_dir, f"{template_name}.yaml")

    if not os.path.exists(template_path):
        raise FileNotFoundError(f"Template not found: {template_path}")

    with open(template_path, 'r', encoding='utf-8') as f:
        config = yaml.safe_load(f)

    return config

def _build_prompt_template(config: Dict[str, Any]) -> ChatPromptTemplate:
    """Build ChatPromptTemplate from configuration."""
    system_message = config.get('system_message', '')
    # support legacy key 'prompt' as an alias for 'human_message'
    human_message = config.get('human_message', '') or config.get('prompt', '')

    if not human_message:
        raise ValueError("human_message is required in template")

    messages = []
    if system_message:
        messages.append(("system", system_message))
    messages.append(("human", human_message))

    return ChatPromptTemplate.from_messages(messages)

def _build_chain(llm, prompt_template: ChatPromptTemplate, config: Dict[str, Any]):
    """Build the LangChain runnable chain."""
    # Add output parser if specified
    output_parser = config.get('output_parser', 'json')
    if output_parser == 'json':
        parser = JsonOutputParser()
    else:
        parser = None

    # Build the chain
    chain = prompt_template | llm

    if parser:
        chain = chain | parser

    return chain

def _extract_inputs(state: Dict[str, Any], config: Dict[str, Any]) -> Dict[str, Any]:
    """Extract required inputs from state based on template configuration."""
    input_keys = config.get('input_keys', [])
    inputs = {}

    for key in input_keys:
        if key in state:
            inputs[key] = make_serializable(state[key])
        else:
            # Try to get from nested state
            inputs[key] = make_serializable(_get_nested_value(state, key))

    return inputs

def _update_state(state: Dict[str, Any], result: Any, config: Dict[str, Any]) -> Dict[str, Any]:
    """Update state with the result of the agent execution."""
    output_key = config.get('output_key', 'result')

    # Deep copy state to avoid mutation
    new_state = state.copy()

    # Store result in state
    new_state[output_key] = result

    # Add to trace if tracing is enabled
    if 'trace' in new_state:
        trace_entry = {
            'agent': config.get('name', 'unknown_agent'),
            'template': config.get('template_name', 'unknown'),
            'result': result
        }
        new_state['trace'].append(trace_entry)

    return new_state

def _get_nested_value(obj: Any, key: str) -> Any:
    """Get nested value from object using dot notation."""
    keys = key.split('.')
    current = obj

    for k in keys:
        if isinstance(current, dict):
            current = current.get(k)
        elif hasattr(current, k):
            current = getattr(current, k)
        else:
            return None

    return current
