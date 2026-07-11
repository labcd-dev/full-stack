import streamlit as st
# import traceback as _tb
from typing import Any, Dict

st.set_page_config(layout="wide")

from frontend_streamlit.ga_agent_ui.ga_agent_home import display_home_page, run_worker_ui
from frontend_streamlit.ga_agent_ui.ga_agent_project import display_project_page
from frontend_streamlit.home_page_style import import_home_page_css_style
from frontend_streamlit.ga_agent_ui.ga_agent_utils import display_logo_home
from frontend_streamlit.mulo_designer_utils import display_edit_case_study_page

from backend_api.MuloDesigner.GaAgent.src.callbacks import register_callback, unregister_callback


def _run_experiment_worker(
    designer, event_queue) -> None:
    """
    Runs inside a daemon thread.
    1. Registers a progress callback with the thread-local registry.
    2. Calls run_ga_handler (blocking).
    3. Emits 'run_complete' or 'run_error' when finished.
    """

    def _push(event: Dict[str, Any]) -> None:
        """Non-blocking put; silently drop if queue is unexpectedly full."""
        try:
            event_queue.put_nowait(event)
        except Exception:
            pass

    register_callback(_push)
    # try:
    final_state = designer.design_controller()
    _push({"event_type": "run_complete", "final_state": final_state})
    # except Exception as exc:
    #     _push({
    #         "event_type": "run_error",
    #         "error": str(exc),
    #         "traceback": _tb.format_exc(),
    #     })
    # finally:
    unregister_callback()


if "mulo_designer_stage" not in st.session_state:
    st.session_state["mulo_designer_stage"] = "setup"
if "selected_pipeline" not in st.session_state:
    st.session_state["selected_pipeline"] = "muloDesign"

import_home_page_css_style()

display_logo_home()

st.markdown(
    "<h1 style='text-align:center;margin-bottom:2px;'>Multi Loop Design</h1>"
    "<p style='text-align:center;color:gray;margin-top:0;'>"
    "LLM-Enhanced Genetic Algorithm for PID controller design"
    "</p>",
    unsafe_allow_html=True,
)
st.markdown("---")

if st.session_state["mulo_designer_stage"] == "setup":
    display_home_page(False)
elif st.session_state["mulo_designer_stage"] == "edit_case_study":
    display_edit_case_study_page()
elif st.session_state["mulo_designer_stage"] == "run_designer":
    st.session_state["mulo_designer_stage"] = "project_page"
    run_worker_ui(_run_experiment_worker)
else:
    display_project_page(False)
    if st.session_state["mulo_designer_stage"] == "optimisation_complete":
        designer = st.session_state["designer"]
        is_complete = designer.controller_index >= len(designer.controller_structure)

        if not is_complete:
            st.markdown('<div id="red_btn"></div>', unsafe_allow_html=True)
            if st.button(f"ðŸš€ Continue Controller Design (Loop {designer.controller_index + 1})", type="primary",
                         use_container_width=True):
                st.session_state["mulo_designer_stage"] = "run_designer"
                designer.equation = st.session_state["modified_code"]
                designer.controller_structure = st.session_state["modified_controller_structure"]
                st.rerun()
                # import pprint
                # pprint.pprint(designer.controller_structure)
                # print(100 * "_")
                # pprint.pprint(designer.equation)
