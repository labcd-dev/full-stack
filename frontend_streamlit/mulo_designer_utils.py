import streamlit as st
import re
import plotly.graph_objects as go
import copy

from backend_api.MuloDesigner.controller_tuning import (
    active_controller_index,
    apply_pid_gains_to_controller_structure,
    controller_loop_name,
    get_pid_gain_bounds,
    get_pid_gains,
    replace_last_pid_controller_gains,
)
from backend_api.MuloDesigner.simulation_utils import simulate_system_response


def generate_controller_name():
    designer = st.session_state["designer"]
    return controller_loop_name(designer.controller_structure, designer.controller_index)


def show_performance_plots():
    designer = st.session_state["designer"]

    # 1. Initialize scratchpad state variables if they don't exist yet
    if "modified_code" not in st.session_state:
        st.session_state["modified_code"] = designer.equation
    if "modified_controller_structure" not in st.session_state:
        st.session_state["modified_controller_structure"] = copy.deepcopy(designer.controller_structure)

    col1, col2 = st.columns([2, 6])
    with col1:
        # Pass the scratchpad structure context explicitly down to the sliders
        code, new_kp, new_ki, new_kd = _show_constant_slidebars(
            designer,
            st.session_state["modified_code"],
            st.session_state["modified_controller_structure"]
        )

        st.markdown('<div id="blue_btn"></div>', unsafe_allow_html=True)
        if st.button("ðŸ’¾ Apply New Values To Controller", type="secondary", use_container_width=True):
            _save_changes(code, new_kp, new_ki, new_kd)

        st.markdown('<div id="blue_btn"></div>', unsafe_allow_html=True)
        if st.button("â®ï¸ Reset To Original Values", type="secondary", use_container_width=True):
            _reset_values()

    with col2:
        # Render the performance plots dynamically using the current code state
        _show_performance_plots(designer, code, st.session_state["modified_controller_structure"])


def _save_changes(code, new_kp, new_ki, new_kd):
    designer = st.session_state["designer"]

    st.session_state["modified_code"] = code
    st.session_state["modified_controller_structure"] = apply_pid_gains_to_controller_structure(
        st.session_state["modified_controller_structure"],
        designer.controller_index,
        new_kp,
        new_ki,
        new_kd,
    )

    st.success("ðŸ’¾ Changes temporarily applied to session scratchpad!")
    st.rerun()


def _reset_values():
    designer = st.session_state["designer"]
    cont_index = max(0, designer.controller_index - 1)

    # 1. Reset the scratchpad to the designer's current (original) values
    st.session_state["modified_code"] = designer.equation
    st.session_state["modified_controller_structure"] = copy.deepcopy(designer.controller_structure)

    # 2. Signal that sliders should be reset on the next render
    st.session_state["reset_sliders"] = True

    st.info("â®ï¸ Reset scratchpad back to original optimization settings.")
    st.rerun()


def _show_constant_slidebars(designer, code, controller_structure):
    cont_index = active_controller_index(designer.controller_index)
    kp, ki, kd = get_pid_gains(controller_structure, designer.controller_index)

    # --- Handle reset flag ---
    if st.session_state.get("reset_sliders", False):
        # Set the slider keys to the original (now current) values BEFORE creating the widgets
        st.session_state[f"kp_slider_{cont_index}"] = kp
        st.session_state[f"ki_slider_{cont_index}"] = ki
        st.session_state[f"kd_slider_{cont_index}"] = kd
        st.session_state["reset_sliders"] = False   # clear the flag

    kp_bound, ki_bound, kd_bound = get_pid_gain_bounds(designer.final_state)

    # Generate sliders with unique keys tied to the loop index
    new_kp = st.slider("Proportional Gain (Kp)", min_value=-kp_bound, max_value=kp_bound, value=kp, step=0.01,
                       key=f"kp_slider_{cont_index}")
    new_ki = st.slider("Integral Gain (Ki)", min_value=-ki_bound, max_value=ki_bound, value=ki, step=0.01,
                       key=f"ki_slider_{cont_index}")
    new_kd = st.slider("Derivative Gain (Kd)", min_value=-kd_bound, max_value=kd_bound, value=kd, step=0.01,
                       key=f"kd_slider_{cont_index}")

    code = replace_last_pid_controller_gains(code, new_kp, new_ki, new_kd)

    return code, new_kp, new_ki, new_kd


def _show_performance_plots(designer, code, controller):
    cont_index = max(0, designer.controller_index - 1)
    y_label = controller[cont_index]["controllers"][0]["controlled_variable"]

    test_signals = ["Step", "Ramp", "Sine"]
    for signal_type in test_signals:
        with st.spinner(f"Simulating final system response to a {signal_type} Input..."):
            cont_index = designer.controller_index - 1
            input_channel_name = controller[cont_index]["controllers"][0]["controlled_variable_in_equation"].capitalize()
            unit = controller[cont_index]["controllers"][0]["target"]["unit"].capitalize()

            # try:
            t, y, ref_val = simulate_system_response(
                code,
                designer.case_study,
                input_channel_name,
                signal_type
            )

            match = re.search(r'\d+', input_channel_name)
            n = int(match.group())

            fig = go.Figure()

            # 1. Add the Actual Value (y) - Solid Line
            fig.add_trace(go.Scatter(
                x=t,
                y=y[:, n],
                # y=traj1,
                mode='lines',
                name=f'{signal_type} Actual Value',
                line=dict(color='blue', width=2)  # Solid blue line
            ))

            # 2. Add the Reference Setpoint (ref_val) - Dashed Line
            fig.add_trace(go.Scatter(
                x=t,
                y=ref_val,
                mode='lines',
                name=f'{signal_type} Reference Setpoint',
                line=dict(dash='dash', color='red', width=2)
            ))

            # 3. Update the layout
            fig.update_layout(
                title=f"System Temporal Tracking Response: {signal_type} Input",
                xaxis_title="Time (seconds)",
                yaxis_title=f"{y_label} ({unit})",
                hovermode="x unified",
                margin=dict(l=20, r=20, t=40, b=20),
                height=380
            )

            # 4. Display the plot in Streamlit
            st.plotly_chart(fig, width='stretch')


def display_edit_case_study_page():
    designer = st.session_state["designer"]

    page_container = st.empty()

    with page_container.container():
        # MUST deepcopy so we don't accidentally mutate the designer object later
        controller_structure = copy.deepcopy(designer.get_controller_structure())
        case_study = copy.deepcopy(designer.get_case_study())

        btn_col1, btn_col2 = st.columns(2)

        with btn_col1:
            st.markdown('<div id="blue_btn"></div>', unsafe_allow_html=True)
            if st.button("â¬…ï¸ Back to Parameter Configurations", type="secondary", use_container_width=True, key="btn_back_to_params"):
                st.session_state["mulo_designer_stage"] = "setup"
                st.rerun()

        with btn_col2:
            st.markdown('<div id="blue_btn"></div>', unsafe_allow_html=True)
            if st.button("ðŸ”„ Reset to Default Values", type="secondary", use_container_width=True, key="btn_reset_defaults"):

                # 1. Fetch the PURE defaults directly from the designer
                default_cs = designer.get_case_study()
                default_ctrl = designer.get_controller_structure()

                # 2. OVERWRITE the session state keys with the pure defaults
                st.session_state["sim_bound_dt"] = float(default_cs.get("simulation_params", {}).get("dt", 0.001))
                st.session_state["sim_bound_max_time"] = float(
                    default_cs.get("simulation_params", {}).get("max_time", 50.0))

                for i, pid_loop in enumerate(default_ctrl):
                    metrics = pid_loop.get("metrics", {})
                    st.session_state[f"mse_input_{i}"] = float(metrics.get("mse", 0.001))
                    st.session_state[f"settling_input_{i}"] = float(metrics.get("settling_time", 7.0))
                    st.session_state[f"overshoot_input_{i}"] = float(metrics.get("overshoot", 15.0))
                    st.session_state[f"effort_input_{i}"] = float(metrics.get("control_effort", 0.25))

                # 3. Rerun. The widgets will lock onto the session_state values we just forced.
                st.rerun()

        with st.expander("âš™ï¸ Live Case Study Parametric Modification", expanded=True):
            # Section 1: Global Simulation Parameters
            st.markdown("#### â±ï¸ **Simulation Parameters**")
            sim_col1, sim_col2 = st.columns(2)
            with sim_col1:
                dt = st.number_input("Time Step Size Delta (dt)",
                                     value=float(case_study.get("simulation_params", {}).get("dt", 0.001)),
                                     step=0.0005, min_value=0.0001, max_value=0.1, format="%.4f", key="sim_bound_dt")
            with sim_col2:
                max_time = st.number_input("Maximum Processing Epoch Run Time (s)",
                                           value=float(case_study.get("simulation_params", {}).get("max_time", 50.0)),
                                           step=1.0, min_value=1.0, max_value=300.0, key="sim_bound_max_time")

            case_study["simulation_params"] = {"dt": dt, "max_time": max_time}
            st.markdown("---")

            # Section 2: Loop Specific Metrics
            st.markdown("#### ðŸŽ¯ **Fixed Performance Targets**")
            for i, pid_loop in enumerate(controller_structure):
                st.markdown(f"##### **Loop Context: {pid_loop['loop_name'].replace('_', ' ').title()}**")

                loop_col1, loop_col2 = st.columns(2)
                with loop_col1:
                    mse = st.number_input("Mean Squared Error (mse)",
                                          value=float(pid_loop.get("metrics", {}).get("mse", 0.001)),
                                          step=100.0, min_value=0.0, format="%.3f", key=f"mse_input_{i}")
                    settling_time = st.number_input("Settling Time Threshold (s)",
                                                    value=float(pid_loop.get("metrics", {}).get("settling_time", 7.0)),
                                                    step=0.5, min_value=0.0, key=f"settling_input_{i}")
                with loop_col2:
                    overshoot = st.number_input("Maximum Percentage Overshoot (%)",
                                                value=float(pid_loop.get("metrics", {}).get("overshoot", 15.0)),
                                                step=0.5, min_value=0.0, max_value=100.0, key=f"overshoot_input_{i}")
                    control_effort = st.number_input("Control Effort Penalty Weight",
                                                     value=float(pid_loop.get("metrics", {}).get("control_effort", 0.25)),
                                                     min_value=0.0, step=0.1, key=f"effort_input_{i}")

                controller_structure[i]["metrics"] = {
                    "mse": mse,
                    "settling_time": settling_time,
                    "overshoot": overshoot,
                    "control_effort": control_effort
                }

        st.markdown('<div id="red_btn"></div>', unsafe_allow_html=True)
        if st.button(f"ðŸš€ Run Controller Design Optimization (Loop {designer.controller_index + 1})", type="primary",
                     use_container_width=True, key="btn_run_optimization"):
            # We only apply edits to the actual designer object when they hit "Run"
            designer.set_case_study(case_study)
            designer.set_controller_structure(controller_structure)
            st.session_state["mulo_designer_stage"] = "run_designer"

            page_container.empty()
            st.rerun()
