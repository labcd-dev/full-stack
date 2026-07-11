import streamlit as st
import numpy as np
import tempfile
import os
import plotly.graph_objects as go
from plotly.subplots import make_subplots
from backend_core.SiloDesigner.src.controllers import initialize_state
from backend_core.SiloDesigner.src.systems import create_system

st.title("Manual Controller Tuner")

uploaded_file = st.file_uploader("Upload dynamics file (.py or .m)", type=['py', 'm'])

if uploaded_file is not None:
    with tempfile.NamedTemporaryFile(delete=False, suffix=os.path.splitext(uploaded_file.name)[1]) as tmp:
        tmp.write(uploaded_file.read())
        dynamics_path = tmp.name

    file_type = "Python (.py)" if uploaded_file.name.endswith('.py') else "MATLAB/Octave (.m)"
    matlab_func_name = None
    num_states_input = None
    if file_type == "MATLAB/Octave (.m)":
        matlab_func_name = st.text_input("MATLAB function name", value="dynamics")
        num_states_input = st.number_input("Number of states", min_value=1, max_value=20, value=2)

    col1, col2 = st.columns(2)
    with col1:
        dt = st.number_input("dt", value=0.01, min_value=0.001)
        max_time = st.number_input("max_time", value=5.0, min_value=0.1)
    with col2:
        target = st.number_input("target", value=0.0)
        # initial_condition_range moved to Scenario Parameters section

    col3, col4 = st.columns(2)
    with col3:
        num_inputs = st.number_input("Number of inputs", value=1, min_value=1, max_value=10)
        input_channel = st.number_input("Input Channel", value=0, min_value=0, max_value=9,
                                        help="Which control input to use (0-indexed)")
    with col4:
        output_channel = st.number_input("Output Channel", value=0, min_value=0, max_value=10,
                                         help="Which state to track (0-indexed)")

    # NEW: Scenario parameters section
    st.subheader("Scenario Parameters")
    col_sc1, col_sc2, col_sc3 = st.columns(3)
    with col_sc1:
        initial_condition_range = st.slider("Initial condition range", -2.0, 2.0, (-1.0, 1.0))
    with col_sc2:
        randomness_level = st.slider("Measurement noise level", 0.0, 0.5, 0.0,
                                     help="Noise added to feedback (randomness_level)")
    with col_sc3:
        disturbance_level = st.slider("Input disturbance level", 0.0, 2.0, 0.0,
                                      help="Disturbance added to control signal (disturbance_level)")

    # Control limits inputs
    col5, col6 = st.columns(2)
    with col5:
        min_ctrl = st.number_input("min_ctrl", value=-10.0, help="Minimum control input limit")
    with col6:
        max_ctrl = st.number_input("max_ctrl", value=10.0, help="Maximum control input limit")

    # Add trim_values input for MIMO
    trim_values_str = st.text_input("Trim values (comma-separated, defaults to zeros)",
                                    value=",".join(["0.0"] * num_inputs),
                                    help="Steady-state inputs for other channels")

    # Parse trim_values
    try:
        trim_values = [float(v.strip()) for v in trim_values_str.split(",") if v.strip()]
        if len(trim_values) != num_inputs:
            trim_values = [0.0] * num_inputs  # Fallback to zeros
            st.warning(f"Invalid trim values; using zeros for {num_inputs} inputs.")
    except ValueError:
        trim_values = [0.0] * num_inputs
        st.warning("Invalid trim values; using zeros.")

    if st.button("Initialize System"):
        try:
            state = initialize_state(
                system_name="custom",
                custom_dynamics_path=dynamics_path,
                file_type=file_type,
                matlab_func_name=matlab_func_name,
                num_states=num_states_input,
                num_inputs=num_inputs,  # Pass num_inputs
                trim_values=trim_values,  # Pass trim_values
                min_ctrl=min_ctrl,  # NEW: Pass min_ctrl
                max_ctrl=max_ctrl,  # NEW: Pass max_ctrl
                max_iter=0,
                dt=dt,
                max_time=max_time,
                target=target,
                input_channel=input_channel,
                output_channel=output_channel,
                monitor=None
            )
            # Apply initial condition range as scenario
            scenario_dict = {
                'initial_condition_range': initial_condition_range,
                'randomness_level': randomness_level,
                'disturbance_level': disturbance_level,
                # 'param_uncertainty': param_uncertainty_value,  # Uncomment/add if implemented in systems.py
            }
            state['simulator'].set_scenario(scenario_dict)
            st.session_state.state = state
            st.session_state.scenario_dict = scenario_dict
            st.session_state.dynamics_path = dynamics_path
            st.session_state.num_inputs = num_inputs  # Store for later use
            st.session_state.trim_values = trim_values
            st.session_state.min_ctrl = min_ctrl  # NEW: Store for potential later use
            st.session_state.max_ctrl = max_ctrl  # NEW: Store for potential later use
            st.success("System initialized!")
        except Exception as e:
            st.error(f"Initialization failed: {e}")

    if 'state' in st.session_state:
        state = st.session_state.state
        system = state['system']
        simulator = state['simulator']

        controllers = ["P", "PI", "PD", "PID", "FSF"]
        controller_type = st.selectbox("Controller Type", controllers, key="ctrl_type")

        schema = system.get_control_param_schema(controller_type)
        param_ranges_ctrl = {k: [v["min"], v["max"]] for k, v in schema.items()}

        # Update manual_gains if necessary
        current_keys = set(param_ranges_ctrl.keys())
        if 'manual_gains' not in st.session_state or set(st.session_state.manual_gains.keys()) != current_keys:
            st.session_state.manual_gains = {k: (v[0] + v[1]) / 2 for k, v in param_ranges_ctrl.items()}

        st.subheader("Gain Sliders")
        updated_gains = {}
        for param_name, rng in sorted(param_ranges_ctrl.items()):
            value = st.slider(
                param_name,
                min_value=float(rng[0]),
                max_value=float(rng[1]),
                value=st.session_state.manual_gains[param_name],
                step=0.01,
                key=f"slider_{param_name}"
            )
            updated_gains[param_name] = value
            st.session_state.manual_gains[param_name] = value

        if st.button("Simulate & Plot"):
            use_fixed_ic = st.checkbox("Use fixed initial condition (overrides scenario range)", value=False)
            fixed_ic = None
            if use_fixed_ic:
                fixed_ic_str = st.text_input("Fixed initial state (comma-separated, length=num_states)",
                                             help="e.g., '1.0,0.0,0.0,0.0' for 4 states")
                try:
                    fixed_ic = np.array([float(v.strip()) for v in fixed_ic_str.split(",") if v.strip()])
                    if len(fixed_ic) != system.num_states:
                        st.warning(
                            f"Fixed IC length {len(fixed_ic)} doesn't match num_states {system.num_states}; using random.")
                        fixed_ic = None
                except ValueError:
                    st.warning("Invalid fixed IC; using random.")
                    fixed_ic = None
            # For MIMO, ensure updated_gains is passed as-is (handled in run_simulation)
            result = simulator.evaluate_parameters(updated_gains, initial_state=fixed_ic)
            if result['success']:
                trajectory = result['trajectory']
                control_signals = result['control_signals']
                # Use stored dt/max_time or system values for time vector
                sim_dt = state.get('dt', dt)
                sim_max_time = state.get('max_time', max_time)
                expected_steps = int(sim_max_time / sim_dt) + 1
                time_points = np.arange(0, sim_max_time + sim_dt, sim_dt)[:expected_steps]
                # Trim if necessary
                if len(trajectory) < len(time_points):
                    time_points = time_points[:len(trajectory)]

                fig = make_subplots(
                    rows=2, cols=1,
                    subplot_titles=['System Response', 'Control Input'],
                    vertical_spacing=0.15
                )
                fig.add_trace(
                    go.Scatter(x=time_points, y=trajectory, mode='lines', name='Response',
                               line=dict(color='rgb(255, 99, 132)', width=2)),
                    row=1, col=1
                )
                fig.add_hline(y=target, line_dash="dash", line_color="green", row=1, col=1, annotation_text="Target")
                fig.add_trace(
                    go.Scatter(x=time_points, y=control_signals, mode='lines', name='Control',
                               line=dict(color='rgb(255, 159, 64)', width=2)),
                    row=2, col=1
                )
                gains_str = ', '.join([f"{k}:{v:.2f}" for k, v in updated_gains.items()])
                fig.update_layout(
                    height=700,
                    showlegend=True,
                    title=f"{controller_type} | Gains: {gains_str}"
                )
                fig.update_xaxes(title_text="Time (s)", row=2, col=1)
                fig.update_yaxes(title_text="Output", row=1, col=1)
                fig.update_yaxes(title_text="Control Signal", row=2, col=1)
                st.plotly_chart(fig, use_container_width=True)

                st.subheader("Metrics")
                metrics = result['metrics']
                col_m1, col_m2 = st.columns(2)
                with col_m1:
                    st.metric("MSE", f"{metrics['mse']:.4f}")
                    st.metric("Settling Time", f"{metrics['settling_time']:.2f}s")
                with col_m2:
                    st.metric("Overshoot (%)", f"{metrics['overshoot']:.2f}")
                    st.metric("Steady-State Error", f"{metrics['ss_error']:.4f}")
            else:
                st.error(f"Simulation failed: {result.get('error', 'Unknown error')}")

    # Cleanup
    if 'dynamics_path' in st.session_state:
        try:
            os.unlink(st.session_state.dynamics_path)
            del st.session_state.dynamics_path
        except:
            pass
else:
    st.info("👆 Upload a dynamics file to begin manual tuning.")