from pathlib import Path
from typing import Any, Dict, List

import streamlit as st

from backend_api.MuloDesigner.GaAgent.data import (
    DEFAULT_OBJECTIVES,
    LLM_MODELS,
    WEB_SEARCH_MODEL_OPTIONS,
    drain_event_queue as drain_backend_event_queue,
    empty_plot_data as build_empty_plot_data,
    get_available_case_studies as get_backend_available_case_studies,
    load_case_study_content,
)

# -- Paths -----------------
REPO_ROOT = Path(__file__).parent
LOGO_PATH = REPO_ROOT / "assets" / "logo.svg"
CASE_STUDIES_DIR = REPO_ROOT / "case_studies" / "json"

# -- Logo helpers ----------

def _svg_content() -> str:
    """Return raw SVG string, or a minimal emoji fallback SVG."""
    if LOGO_PATH.exists():
        return LOGO_PATH.read_text(encoding="utf-8")
    return (
        '<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 64 64">'
        '<text y="0.9em" font-size="56">ðŸŽ›ï¸</text></svg>'
    )


def display_logo_sidebar() -> None:
    """Render the SVG logo in the sidebar (compact)."""
    svg = _svg_content()
    # Inject inline style for extra small sizing
    svg = svg.replace('<svg', '<svg style="width:100%; height:auto; max-width:80px;"', 1)

    st.markdown(
        f'<div style="text-align:center;padding:12px 4px 4px;">'
        f'<div style="max-width:80px;margin:auto;">{svg}</div>'
        f"</div>",
        unsafe_allow_html=True,
    )


def display_logo_home() -> None:
    """Render the SVG logo on the home page (larger)."""
    svg = _svg_content()
    # Inject inline style for small sizing
    svg = svg.replace('<svg', '<svg style="width:100%; height:auto; max-width:160px;"', 1)

    st.markdown(
        f'<div style="display:flex;justify-content:center;padding:28px 0 12px;">'
        f'<div style="max-width:160px;width:100%;">{svg}</div>'
        f"</div>",
        unsafe_allow_html=True,
    )


# -- Case-study helpers --------------------------------------------------------

def get_available_case_studies() -> List[str]:
    """Return sorted list of *.json filenames in case_studies/json/."""
    return get_backend_available_case_studies(CASE_STUDIES_DIR)


def load_case_study_safe(selected_cs: str, run_by_mulo_designer: bool = True) -> Dict[str, Any]:
    """Load a case study via src.utils.load_case_study with graceful error handling."""
    if run_by_mulo_designer:
        return load_case_study_content(selected_cs, run_by_mulo_designer=True)

    try:
        return load_case_study_content(selected_cs, run_by_mulo_designer=False)
    except Exception as exc:
        st.error(f"Failed to load case study '{selected_cs}': {exc}")
        return {}


# -- Plot-data container -------------------------------------------------------

def empty_plot_data() -> Dict[str, Any]:
    """
    Return a freshly initialised container for streaming plot data.

    Per-generation series (one entry per on_generation callback)
    -----------------------------------------------------------
    cumulative_nfe, best_baseline_so_far, mse, settling_time, overshoot,
    control_effort, Kp, Ki, Kd, attempt, success_score

    Per-attempt metadata (dict keyed by attempt number)
    ---------------------------------------------------
    attempt_ranges  : {att: {Kp:[lo,hi], Ki:[lo,hi], Kd:[lo,hi]}}
    attempt_weights : {att: {mse:w, settling_time:w, ...}}
    attempt_pop_gen : {att: {pop:N, gen:G}}

    attempt_boundaries_nfe : cumulative NFE values where the attempt number
                             changes (used for dashed vertical lines).

    attempt_summaries : list of attempt_complete event dicts (one per
                        completed attempt, emitted by evaluate_ga_node).
    """
    return build_empty_plot_data()


# -- Event-queue drain ---------------------------------------------------------

def drain_event_queue() -> None:
    """
    Non-blocking drain of ``st.session_state.event_queue`` into
    ``st.session_state.plot_data`` and session metadata.

    Safe to call on every Streamlit rerun.
    """
    updates = drain_backend_event_queue(st.session_state.get("event_queue"), st.session_state.plot_data)
    for key, value in updates.items():
        st.session_state[key] = value

