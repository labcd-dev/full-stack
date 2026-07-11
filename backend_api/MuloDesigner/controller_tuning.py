"""Pure controller-tuning helpers for Mulo Designer."""

import re
from typing import Any, Dict, List, Tuple


def active_controller_index(controller_index: int) -> int:
    """Return the zero-based active controller index used by the UI workflow."""
    return max(0, controller_index - 1)


def controller_loop_name(controller_structure: List[Dict[str, Any]], controller_index: int) -> str:
    """Return the display name for the active controller loop."""
    cont_index = active_controller_index(controller_index)
    return controller_structure[cont_index]["loop_name"].replace("_", " ")


def get_pid_gains(controller_structure: List[Dict[str, Any]], controller_index: int) -> Tuple[float, float, float]:
    """Return PID gains for the active controller."""
    cont_index = active_controller_index(controller_index)
    controller = controller_structure[cont_index]["controllers"][0]
    return float(controller["kp"]), float(controller["ki"]), float(controller["kd"])


def get_pid_gain_bounds(final_state: Dict[str, Any]) -> Tuple[float, float, float]:
    """Return PID gain bounds from the final optimizer state."""
    param_ranges = final_state["best_result"]["best_ga_config"]["param_ranges"]["PID"]
    return param_ranges["Kp"][1], param_ranges["Ki"][1], param_ranges["Kd"][1]


def replace_last_pid_controller_gains(code: str, kp: float, ki: float, kd: float) -> str:
    """Replace the final PIDController gain tuple in generated controller code."""
    pattern = r"(\bPIDController\()\s*[-]?\d*\.?\d*\s*,\s*[-]?\d*\.?\d*\s*,\s*[-]?\d*\.?\d*"
    matches = list(re.finditer(pattern, code))

    if not matches:
        return code

    last_match = matches[-1]
    start_idx, end_idx = last_match.span()
    prefix = last_match.group(1)
    replacement_segment = rf"{prefix}{kp}, {ki}, {kd}"
    return code[:start_idx] + replacement_segment + code[end_idx:]


def apply_pid_gains_to_controller_structure(
    controller_structure: List[Dict[str, Any]],
    controller_index: int,
    kp: float,
    ki: float,
    kd: float,
) -> List[Dict[str, Any]]:
    """Apply PID gains to the active controller structure and return it."""
    cont_index = active_controller_index(controller_index)
    controller = controller_structure[cont_index]["controllers"][0]
    controller["kp"] = kp
    controller["ki"] = ki
    controller["kd"] = kd
    return controller_structure
