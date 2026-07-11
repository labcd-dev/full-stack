"""Pure helpers for handing off Recommender results to the Trimmer workflow."""

import json
from typing import Any, Dict, Optional

from backend_api.Recommender.functionalNodes.create_controller_graph import (
    find_trimming_parameters,
    get_states_and_inputs,
)


def prepare_trimmer_handoff(
    state_snapshot: Dict[str, Any],
    chosen_controller: Optional[str] = None,
) -> Dict[str, Any]:
    """Build trimmer handoff data from a recommender graph state snapshot."""
    controller_json = state_snapshot["controller_json"]
    chosen = chosen_controller or controller_json["Initial_controller"]
    system_identification = json.loads(state_snapshot["system_identification"])

    return {
        "file_content": state_snapshot["equation"],
        "chosen_controller": chosen,
        "trimming_params": find_trimming_parameters(chosen, system_identification),
        "states_inputs": get_states_and_inputs(system_identification),
    }
