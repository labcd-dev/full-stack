"""Pure helpers for handing off Recommender results to the Trimmer workflow."""

import json
from typing import Any, Dict, Optional

from backend_api.Recommender.functionalNodes.create_controller_graph import (
    find_trimming_parameters,
    get_states_and_inputs,
)


def _as_controller_json_string(value: Any) -> Optional[str]:
    """Normalize a controller value to a JSON object string."""
    if value is None:
        return None
    if isinstance(value, dict):
        return json.dumps(value)
    if isinstance(value, str):
        stripped = value.strip()
        if not stripped:
            return None
        if stripped.startswith("{"):
            return stripped
        return None
    return None


def resolve_controller_json(
    controller_json: Dict[str, Any],
    chosen_controller: Optional[str] = None,
    control_loop_analysis: Optional[str] = None,
) -> str:
    """Resolve a controller key or JSON string to controller structure JSON."""
    if chosen_controller and chosen_controller in controller_json:
        resolved = _as_controller_json_string(controller_json[chosen_controller])
        if resolved:
            return resolved

    if chosen_controller:
        direct = _as_controller_json_string(chosen_controller)
        if direct:
            return direct

    initial = _as_controller_json_string(controller_json.get("Initial_controller"))
    if initial:
        return initial

    for value in controller_json.values():
        resolved = _as_controller_json_string(value)
        if resolved:
            return resolved

    fallback = _as_controller_json_string(control_loop_analysis)
    if fallback:
        return fallback

    raise ValueError("No valid controller JSON found in recommender state")


def prepare_trimmer_handoff(
    state_snapshot: Dict[str, Any],
    chosen_controller: Optional[str] = None,
) -> Dict[str, Any]:
    """Build trimmer handoff data from a recommender graph state snapshot."""
    controller_json = state_snapshot.get("controller_json") or {}
    control_loop_analysis = state_snapshot.get("control_loop_analysis")
    chosen = resolve_controller_json(
        controller_json,
        chosen_controller,
        control_loop_analysis,
    )
    system_identification = json.loads(state_snapshot["system_identification"])

    return {
        "file_content": state_snapshot["equation"],
        "chosen_controller": chosen,
        "trimming_params": find_trimming_parameters(chosen, system_identification),
        "states_inputs": get_states_and_inputs(system_identification),
    }
