"""Pure helpers for Trimmer workflow orchestration."""

import json
import os
from typing import Any, Dict, Optional

import numpy as np

from backend_api.common.serialization import make_serializable


def build_trimmer_initial_state(
    trimming_params: Dict[str, Any],
    file_content: str,
    logger: Any,
    ui_inputs: Optional[Dict[str, Any]] = None,
    *,
    ui_mode: str = "streamlit",
) -> Dict[str, Any]:
    """Build the initial LangGraph state for the Trimmer workflow."""
    return {
        "trimming_params": trimming_params,
        "logger": logger,
        "input_content": file_content,
        "ui_mode": ui_mode,
        "ui_inputs": ui_inputs or {},
        "trace": [],
        "restart_count": 0,
        "max_restarts": 3,
        "final_result": {},
        "config": {},
        "initial_guess": {},
        "strategy": "",
        "x_e": np.array([]),
        "u_e": np.array([]),
        "converged": False,
        "A": np.array([]),
        "B": np.array([]),
    }


def resolve_trimmer_config(final_values: Dict[str, Any]) -> Dict[str, Any]:
    """Resolve the trimmer config from final workflow values."""
    config = final_values.get("config", {})
    if config:
        return config

    for entry in reversed(final_values.get("trace", [])):
        if "config" in entry:
            return entry["config"]

    return {}


def finalize_trimmer_run(
    final_values: Dict[str, Any],
    file_name: str,
    output_dir: str,
) -> Dict[str, Any]:
    """Persist trimmer results and return artifact metadata."""
    result = final_values.get("final_result", {})
    config = resolve_trimmer_config(final_values)

    os.makedirs(output_dir, exist_ok=True)

    with open(os.path.join(output_dir, f"{file_name}_result.json"), "w", encoding="utf-8") as result_file:
        json.dump(make_serializable(result), result_file, indent=2)

    pdf_file = None
    if result and "equilibrium" in result and result["equilibrium"].get("x_e") is not None:
        pdf_file = os.path.join(output_dir, f"{file_name}_report.pdf")

    return {
        "result": result,
        "config": config,
        "pdf_file": pdf_file,
        "safe_system_name": file_name,
        "output_dir": output_dir,
    }
