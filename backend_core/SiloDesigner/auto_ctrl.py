import streamlit as st
import numpy as np
import tempfile
import os
import plotly.graph_objects as go
from plotly.subplots import make_subplots
from scipy import signal
from scipy.optimize import minimize
import pygad
from backend_core.SiloDesigner.src.controllers import initialize_state
from backend_core.SiloDesigner.src.systems import create_system

st.title("Automated Controller Design")
st.markdown("Upload a dynamics file and automatically design PID or LQR controllers")

# File upload
uploaded_file = st.file_uploader("Upload dynamics file (.py or .m)", type=['py', 'm'])

if uploaded_file is not None:
    with tempfile.NamedTemporaryFile(delete=False, suffix=os.path.splitext(uploaded_file.name)[1]) as tmp:
        tmp.write(uploaded_file.read())
        dynamics_path = tmp.name

    file_type = "Python (.py)" if uploaded_file.name.endswith('.py') else "MATLAB/Octave (.m)"

    # MATLAB-specific inputs
    matlab_func_name = None
    num_states_input = None
    if file_type == "MATLAB/Octave (.m)":
        matlab_func_name = st.text_input("MATLAB function name", value="dynamics")
        num_states_input = st.number_input("Number of states", min_value=1, max_value=20, value=2)

    # System parameters
    col1, col2 = st.columns(2)
    with col1:
        dt = st.number_input("Time step (dt)", value=0.01, min_value=0.001, format="%.4f")
        max_time = st.number_input("Simulation time", value=5.0, min_value=0.1)
        target = st.number_input("Target setpoint", value=0.0)
    with col2:
        num_inputs = st.number_input("Number of inputs", value=1, min_value=1, max_value=10)
        input_channel = st.number_input("Input Channel", value=0, min_value=0, max_value=9,
                                        help="Which control input to use (0-indexed)")
        output_channel = st.number_input("Output Channel", value=0, min_value=0, max_value=10,
                                         help="Which state to track (0-indexed)")

    # Scenario parameters
    st.subheader("Scenario Parameters")
    col_sc1, col_sc2, col_sc3 = st.columns(3)
    with col_sc1:
        initial_condition_range = st.slider("Initial condition range", -2.0, 2.0, (-1.0, 1.0))
    with col_sc2:
        randomness_level = st.slider("Measurement noise", 0.0, 0.5, 0.0)
    with col_sc3:
        disturbance_level = st.slider("Input disturbance", 0.0, 2.0, 0.0)

    # Control limits
    col5, col6 = st.columns(2)
    with col5:
        min_ctrl = st.number_input("Min control limit", value=-10.0)
    with col6:
        max_ctrl = st.number_input("Max control limit", value=10.0)

    # Trim values
    trim_values_str = st.text_input("Trim values (comma-separated)",
                                    value=",".join(["0.0"] * num_inputs),
                                    help="Steady-state inputs for other channels")
    try:
        trim_values = [float(v.strip()) for v in trim_values_str.split(",") if v.strip()]
        if len(trim_values) != num_inputs:
            trim_values = [0.0] * num_inputs
            st.warning(f"Invalid trim values; using zeros for {num_inputs} inputs.")
    except ValueError:
        trim_values = [0.0] * num_inputs
        st.warning("Invalid trim values; using zeros.")

    # Controller selection
    st.subheader("Controller Design Method")
    previous_mode = st.session_state.get('controller_mode', None)
    controller_mode = st.radio("Select controller type:", ["PID", "FSF"], key="controller_mode_radio")
    if previous_mode != controller_mode:
        if 'designed_controller' in st.session_state:
            del st.session_state.designed_controller
        if 'opt_history' in st.session_state:
            del st.session_state.opt_history
        if 'tune_method' in st.session_state:
            del st.session_state.tune_method
        if 'design_method' in st.session_state:
            del st.session_state.design_method
    st.session_state.controller_mode = controller_mode

    # Initialize system button
    if st.button("Initialize System"):
        try:
            state = initialize_state(
                system_name="custom",
                custom_dynamics_path=dynamics_path,
                file_type=file_type,
                matlab_func_name=matlab_func_name,
                num_states=num_states_input,
                num_inputs=num_inputs,
                trim_values=trim_values,
                min_ctrl=min_ctrl,
                max_ctrl=max_ctrl,
                max_iter=0,
                dt=dt,
                max_time=max_time,
                target=target,
                input_channel=input_channel,
                output_channel=output_channel,
                monitor=None
            )
            scenario_dict = {
                'initial_condition_range': initial_condition_range,
                'randomness_level': randomness_level,
                'disturbance_level': disturbance_level,
            }
            state['simulator'].set_scenario(scenario_dict)
            st.session_state.state = state
            st.session_state.dynamics_path = dynamics_path
            # Reset design on re-initialize
            if 'designed_controller' in st.session_state:
                del st.session_state.designed_controller
            if 'opt_history' in st.session_state:
                del st.session_state.opt_history
            if 'tune_method' in st.session_state:
                del st.session_state.tune_method
            if 'design_method' in st.session_state:
                del st.session_state.design_method
            st.success(f"✅ System initialized! ({state['system'].num_states} states)")
        except Exception as e:
            st.error(f"Initialization failed: {e}")

    # Controller design section
    if 'state' in st.session_state:
        state = st.session_state.state
        system = state['system']
        simulator = state['simulator']

        st.divider()
        st.subheader(f"Design {st.session_state.controller_mode} Controller")

        if st.session_state.controller_mode == "PID":
            st.markdown("**PID Auto-Tuning Parameters**")
            col_pid1, col_pid2 = st.columns(2)
            with col_pid1:
                tune_method = st.selectbox("Tuning method",
                                           ["Ziegler-Nichols", "Gradient-based Optimization",
                                            "Genetic Algorithm (PyGAD)"])
                num_samples = st.number_input("Evaluation samples", value=10, min_value=5, max_value=50,
                                              help="Number of random ICs for performance evaluation")
            with col_pid2:
                Kp_range = st.slider("Kp search range", 0.0, 100.0, (1.0, 50.0))
                Ki_range = st.slider("Ki search range", 0.0, 20.0, (0.01, 5.0))
                Kd_range = st.slider("Kd search range", 0.0, 20.0, (0.01, 10.0))

            # Weight sliders for multi-objective optimization
            with st.expander("🎯 Optimization Weights"):
                w_mse = st.slider("MSE weight", 0.0, 10.0, 1.0, 0.1)
                w_settling = st.slider("Settling time weight", 0.0, 1.0, 0.1, 0.01)
                w_overshoot = st.slider("Overshoot weight", 0.0, 1.0, 0.01, 0.001)
                w_control = st.slider("Control effort weight", 0.0, 0.1, 0.001, 0.0001)

            # Advanced settings
            with st.expander("⚙️ Advanced Optimizer Settings"):
                if tune_method == "Gradient-based Optimization":
                    maxiter = st.number_input("Max iterations", value=30, min_value=10, max_value=100)
                elif tune_method == "Genetic Algorithm (PyGAD)":
                    num_generations = st.number_input("Generations", value=20, min_value=5, max_value=50)
                    sol_per_pop = st.number_input("Population size", value=10, min_value=5, max_value=50)
                else:
                    st.info("No advanced settings for Ziegler-Nichols.")

            if st.button("🔧 Design PID Controller", type="primary"):
                progress_bar = st.progress(0)
                status_text = st.empty()

                # Containers for visualization
                opt_history = {'iteration': [], 'cost': [], 'Kp': [], 'Ki': [], 'Kd': []}

                # Define objective function
                def objective(params):
                    Kp, Ki, Kd = params
                    total_cost = 0
                    valid_runs = 0

                    for _ in range(num_samples):
                        result = simulator.evaluate_parameters({'Kp': Kp, 'Ki': Ki, 'Kd': Kd})
                        if result['success']:
                            metrics = result['metrics']

                            # Check for NaN or Inf in metrics before using them
                            if (np.isnan(metrics['mse']) or np.isinf(metrics['mse']) or
                                    np.isnan(metrics['settling_time']) or np.isinf(metrics['settling_time']) or
                                    np.isnan(metrics['overshoot']) or np.isinf(metrics['overshoot']) or
                                    np.isnan(metrics['control_effort']) or np.isinf(metrics['control_effort'])):
                                total_cost += 10000  # Large penalty for invalid metrics
                            else:
                                cost = (w_mse * metrics['mse'] +
                                        w_settling * metrics['settling_time'] +
                                        w_overshoot * metrics['overshoot'] / 100.0 +
                                        w_control * metrics['control_effort'] / 1000.0)
                                total_cost += cost
                                valid_runs += 1
                        else:
                            total_cost += 10000  # Penalty for failed simulation

                    # Ensure we don't return NaN
                    if valid_runs == 0:
                        return 10000  # Return large penalty if all runs failed
                    return total_cost / valid_runs

                with st.spinner(f"Tuning PID controller using {tune_method}..."):
                    if tune_method == "Gradient-based Optimization":
                        bounds = [(Kp_range[0], Kp_range[1]),
                                  (Ki_range[0], Ki_range[1]),
                                  (Kd_range[0], Kd_range[1])]
                        x0 = [np.mean(Kp_range), np.mean(Ki_range), np.mean(Kd_range)]

                        # Wrapper to track progress
                        def objective_tracked(params):
                            cost = objective(params)
                            opt_history['iteration'].append(len(opt_history['iteration']) + 1)
                            opt_history['cost'].append(cost)
                            opt_history['Kp'].append(params[0])
                            opt_history['Ki'].append(params[1])
                            opt_history['Kd'].append(params[2])
                            progress_bar.progress(min(len(opt_history['iteration']) / maxiter, 1.0))
                            status_text.text(f"Iteration {len(opt_history['iteration'])}: Cost = {cost:.4f}")
                            return cost

                        result_opt = minimize(objective_tracked, x0, method='L-BFGS-B', bounds=bounds,
                                              options={'maxiter': maxiter})

                        Kp_opt, Ki_opt, Kd_opt = result_opt.x
                        status_text.text(f"Optimization completed in {result_opt.nit} iterations")

                    elif tune_method == "Genetic Algorithm (PyGAD)":
                        # PyGAD configuration

                        # Define fitness function for PyGAD (minimize cost -> maximize negative cost)
                        def fitness_func(ga_instance, solution, solution_idx):
                            cost = objective(solution)

                            # PyGAD requires valid fitness values
                            # Convert cost to fitness (minimize cost = maximize negative cost)
                            if np.isnan(cost) or np.isinf(cost):
                                return -10000  # Large negative fitness for invalid solutions
                            return -cost

                        # Callback to track progress
                        def on_generation(ga_instance):
                            generation = ga_instance.generations_completed
                            solution, solution_fitness, _ = ga_instance.best_solution()
                            cost = -solution_fitness  # Convert back to cost

                            opt_history['iteration'].append(generation)
                            opt_history['cost'].append(cost)
                            opt_history['Kp'].append(solution[0])
                            opt_history['Ki'].append(solution[1])
                            opt_history['Kd'].append(solution[2])

                            progress_bar.progress(min(generation / num_generations, 1.0))
                            status_text.text(f"Generation {generation}/{num_generations}: Best Cost = {cost:.4f}")

                        # Initialize PyGAD
                        ga_instance = pygad.GA(
                            num_generations=num_generations,
                            num_parents_mating=4,
                            fitness_func=fitness_func,
                            sol_per_pop=sol_per_pop,
                            num_genes=3,
                            gene_space=[
                                {'low': Kp_range[0], 'high': Kp_range[1]},
                                {'low': Ki_range[0], 'high': Ki_range[1]},
                                {'low': Kd_range[0], 'high': Kd_range[1]}
                            ],
                            parent_selection_type="sss",
                            keep_parents=2,
                            crossover_type="single_point",
                            mutation_type="random",
                            mutation_num_genes=1,
                            on_generation=on_generation,
                            random_seed=42
                        )

                        ga_instance.run()
                        solution, solution_fitness, _ = ga_instance.best_solution()
                        Kp_opt, Ki_opt, Kd_opt = solution

                        status_text.text(f"GA completed: {num_generations} generations, cost = {-solution_fitness:.4f}")

                    else:  # Ziegler-Nichols
                        progress_bar.progress(0.5)
                        status_text.text("Applying Ziegler-Nichols rules...")

                        Ku = np.mean(Kp_range)
                        Tu = 1.0

                        Kp_opt = 0.6 * Ku
                        Ki_opt = 2 * Kp_opt / Tu
                        Kd_opt = Kp_opt * Tu / 8

                        Kp_opt = np.clip(Kp_opt, Kp_range[0], Kp_range[1])
                        Ki_opt = np.clip(Ki_opt, Ki_range[0], Ki_range[1])
                        Kd_opt = np.clip(Kd_opt, Kd_range[0], Kd_range[1])
                        status_text.text("Ziegler-Nichols tuning completed")

                    progress_bar.progress(1.0)

                    st.session_state.designed_controller = {
                        'Kp': Kp_opt,
                        'Ki': Ki_opt,
                        'Kd': Kd_opt
                    }
                    st.session_state.opt_history = opt_history
                    st.session_state.tune_method = tune_method

            # Persistent display for PID design results
            if 'designed_controller' in st.session_state and st.session_state.controller_mode == "PID":
                Kp_opt = st.session_state.designed_controller['Kp']
                Ki_opt = st.session_state.designed_controller['Ki']
                Kd_opt = st.session_state.designed_controller['Kd']
                opt_history = st.session_state.opt_history
                tune_method = st.session_state.tune_method

                st.success(f"✅ PID Controller Designed!")
                col_gain1, col_gain2, col_gain3 = st.columns(3)
                with col_gain1:
                    st.metric("Kp", f"{Kp_opt:.4f}")
                with col_gain2:
                    st.metric("Ki", f"{Ki_opt:.4f}")
                with col_gain3:
                    st.metric("Kd", f"{Kd_opt:.4f}")

                # Visualization of optimization progress
                if opt_history['iteration']:
                    st.subheader("Optimization Progress")

                    fig_opt = make_subplots(
                        rows=2, cols=2,
                        subplot_titles=['Cost Function', 'Kp Evolution', 'Ki Evolution', 'Kd Evolution'],
                        vertical_spacing=0.15,
                        horizontal_spacing=0.1
                    )

                    # Cost evolution
                    fig_opt.add_trace(
                        go.Scatter(x=opt_history['iteration'], y=opt_history['cost'],
                                   mode='lines+markers', name='Cost',
                                   line=dict(color='red', width=2)),
                        row=1, col=1
                    )

                    # Parameter evolutions
                    fig_opt.add_trace(
                        go.Scatter(x=opt_history['iteration'], y=opt_history['Kp'],
                                   mode='lines+markers', name='Kp',
                                   line=dict(color='blue', width=2)),
                        row=1, col=2
                    )
                    fig_opt.add_trace(
                        go.Scatter(x=opt_history['iteration'], y=opt_history['Ki'],
                                   mode='lines+markers', name='Ki',
                                   line=dict(color='green', width=2)),
                        row=2, col=1
                    )
                    fig_opt.add_trace(
                        go.Scatter(x=opt_history['iteration'], y=opt_history['Kd'],
                                   mode='lines+markers', name='Kd',
                                   line=dict(color='orange', width=2)),
                        row=2, col=2
                    )

                    fig_opt.update_xaxes(title_text="Iteration", row=1, col=1)
                    fig_opt.update_xaxes(title_text="Iteration", row=1, col=2)
                    fig_opt.update_xaxes(title_text="Iteration", row=2, col=1)
                    fig_opt.update_xaxes(title_text="Iteration", row=2, col=2)

                    fig_opt.update_yaxes(title_text="Cost", row=1, col=1)
                    fig_opt.update_yaxes(title_text="Kp", row=1, col=2)
                    fig_opt.update_yaxes(title_text="Ki", row=2, col=1)
                    fig_opt.update_yaxes(title_text="Kd", row=2, col=2)

                    fig_opt.update_layout(height=600, showlegend=False,
                                          title_text=f"{tune_method} Progress")

                    st.plotly_chart(fig_opt, use_container_width=True)

        else:  # FSF
            st.markdown("**Full-State Feedback Design**")

            design_method = st.radio("Design method:",
                                     ["LQR (requires linearization)",
                                      "Gradient-based Optimization",
                                      "Genetic Algorithm (PyGAD)"])

            n_states = system.num_states

            if design_method == "LQR (requires linearization)":
                st.info("For LQR design, provide linearized system matrices A and B, and weight matrices Q and R.")

                col_lqr1, col_lqr2 = st.columns(2)
                with col_lqr1:
                    st.markdown("**System Matrices**")
                    A_input = st.text_area("Matrix A (comma-separated rows, semicolon-separated)",
                                           value="; ".join([", ".join(["0"] * n_states) for _ in range(n_states)]),
                                           height=100)
                    B_input = st.text_area("Matrix B (comma-separated)",
                                           value="; ".join(["0" for _ in range(n_states - 1)] + ["1"]),
                                           height=100)

                with col_lqr2:
                    st.markdown("**Weight Matrices**")
                    Q_input = st.text_area("Matrix Q (state weights)",
                                           value="; ".join([", ".join(["1" if i == j else "0"
                                                                       for j in range(n_states)])
                                                            for i in range(n_states)]),
                                           height=100)
                    R_input = st.text_input("Scalar R (control weight)", value="0.1")

                if st.button("🔧 Design LQR Controller", type="primary"):
                    try:
                        A = np.array([[float(x) for x in row.split(',')]
                                      for row in A_input.split(';')])
                        B = np.array([[float(x)] for x in B_input.split(';')])
                        Q = np.array([[float(x) for x in row.split(',')]
                                      for row in Q_input.split(';')])
                        R = np.array([[float(R_input)]])

                        if A.shape != (n_states, n_states):
                            st.error(f"Matrix A must be {n_states}x{n_states}")
                        elif B.shape != (n_states, 1):
                            st.error(f"Matrix B must be {n_states}x1")
                        elif Q.shape != (n_states, n_states):
                            st.error(f"Matrix Q must be {n_states}x{n_states}")
                        else:
                            from scipy.linalg import solve_continuous_are

                            with st.spinner("Solving LQR problem..."):
                                P = solve_continuous_are(A, B, Q, R)
                                K = np.linalg.inv(R) @ B.T @ P
                                K = K.flatten()

                                controller_params = {f'K{i + 1}': K[i] for i in range(n_states)}
                                st.session_state.designed_controller = controller_params
                                st.session_state.design_method = design_method

                                st.success("✅ LQR Controller Designed!")
                                st.write("**State Feedback Gains:**")
                                cols = st.columns(min(n_states, 4))
                                for i, k_val in enumerate(K):
                                    with cols[i % len(cols)]:
                                        st.metric(f"K{i + 1}", f"{k_val:.4f}")

                    except Exception as e:
                        st.error(f"LQR design failed: {e}")

            else:  # Optimization-based FSF
                st.markdown("**Gain Search Ranges**")
                K_ranges = {}
                cols = st.columns(min(n_states, 3))
                for i in range(n_states):
                    with cols[i % len(cols)]:
                        K_ranges[f'K{i + 1}'] = st.slider(f"K{i + 1} range",
                                                          -50.0, 50.0, (-10.0, 10.0),
                                                          key=f"K{i + 1}_range")

                num_samples = st.number_input("Evaluation samples", value=10, min_value=5, max_value=50,
                                              key="fsf_samples")

                with st.expander("🎯 Optimization Weights"):
                    w_mse = st.slider("MSE weight", 0.0, 10.0, 1.0, 0.1, key="fsf_w_mse")
                    w_settling = st.slider("Settling time weight", 0.0, 1.0, 0.1, 0.01, key="fsf_w_settling")
                    w_overshoot = st.slider("Overshoot weight", 0.0, 1.0, 0.01, 0.001, key="fsf_w_overshoot")
                    w_control = st.slider("Control effort weight", 0.0, 0.1, 0.001, 0.0001, key="fsf_w_control")

                # Advanced settings
                with st.expander("⚙️ Advanced Optimizer Settings"):
                    if design_method == "Gradient-based Optimization":
                        maxiter = st.number_input("Max iterations", value=30, min_value=10, max_value=100, key="fsf_maxiter")
                    else:  # GA
                        num_generations = st.number_input("Generations", value=20, min_value=5, max_value=50, key="fsf_ngen")
                        sol_per_pop = st.number_input("Population size", value=15, min_value=5, max_value=50, key="fsf_pop")

                if st.button("🔧 Design FSF Controller", type="primary"):
                    progress_bar = st.progress(0)
                    status_text = st.empty()

                    opt_history = {'iteration': [], 'cost': []}
                    for i in range(n_states):
                        opt_history[f'K{i + 1}'] = []

                    def objective_fsf(params):
                        controller_params = {f'K{i + 1}': params[i] for i in range(n_states)}
                        total_cost = 0
                        valid_runs = 0

                        for _ in range(num_samples):
                            result = simulator.evaluate_parameters(controller_params)
                            if result['success']:
                                metrics = result['metrics']

                                # Check for NaN or Inf in metrics
                                if (np.isnan(metrics['mse']) or np.isinf(metrics['mse']) or
                                        np.isnan(metrics['settling_time']) or np.isinf(metrics['settling_time']) or
                                        np.isnan(metrics['overshoot']) or np.isinf(metrics['overshoot']) or
                                        np.isnan(metrics['control_effort']) or np.isinf(metrics['control_effort'])):
                                    total_cost += 10000
                                else:
                                    cost = (w_mse * metrics['mse'] +
                                            w_settling * metrics['settling_time'] +
                                            w_overshoot * metrics['overshoot'] / 100.0 +
                                            w_control * metrics['control_effort'] / 1000.0)
                                    total_cost += cost
                                    valid_runs += 1
                            else:
                                total_cost += 10000

                        if valid_runs == 0:
                            return 10000
                        return total_cost / valid_runs

                    bounds = [K_ranges[f'K{i + 1}'] for i in range(n_states)]

                    with st.spinner(f"Optimizing FSF gains using {design_method}..."):
                        if design_method == "Gradient-based Optimization":
                            x0 = [np.mean(bounds[i]) for i in range(n_states)]

                            def objective_tracked(params):
                                cost = objective_fsf(params)
                                opt_history['iteration'].append(len(opt_history['iteration']) + 1)
                                opt_history['cost'].append(cost)
                                for i in range(n_states):
                                    opt_history[f'K{i + 1}'].append(params[i])
                                progress_bar.progress(min(len(opt_history['iteration']) / maxiter, 1.0))
                                status_text.text(f"Iteration {len(opt_history['iteration'])}: Cost = {cost:.4f}")
                                return cost

                            result_opt = minimize(objective_tracked, x0, method='L-BFGS-B',
                                                  bounds=bounds, options={'maxiter': maxiter})

                            K_opt = result_opt.x
                            status_text.text(f"Optimization completed in {result_opt.nit} iterations")

                        else:  # PyGAD
                            # Define fitness function for PyGAD (minimize cost -> maximize negative cost)
                            def fitness_func(ga_instance, solution, solution_idx):
                                cost = objective_fsf(solution)

                                # PyGAD requires valid fitness values
                                # Convert cost to fitness (minimize cost = maximize negative cost)
                                if np.isnan(cost) or np.isinf(cost):
                                    return -10000  # Large negative fitness for invalid solutions
                                return -cost

                            # Callback to track progress
                            def on_generation(ga_instance):
                                generation = ga_instance.generations_completed
                                solution, solution_fitness, _ = ga_instance.best_solution()
                                cost = -solution_fitness

                                opt_history['iteration'].append(generation)
                                opt_history['cost'].append(cost)
                                for i in range(n_states):
                                    opt_history[f'K{i + 1}'].append(solution[i])

                                progress_bar.progress(min(generation / num_generations, 1.0))
                                status_text.text(f"Generation {generation}/{num_generations}: Best Cost = {cost:.4f}")

                            gene_space = [{'low': bounds[i][0], 'high': bounds[i][1]} for i in range(n_states)]

                            ga_instance = pygad.GA(
                                num_generations=num_generations,
                                num_parents_mating=5,
                                fitness_func=fitness_func,
                                sol_per_pop=sol_per_pop,
                                num_genes=n_states,
                                gene_space=gene_space,
                                parent_selection_type="sss",
                                keep_parents=2,
                                crossover_type="single_point",
                                mutation_type="random",
                                mutation_num_genes=1,
                                on_generation=on_generation,
                                random_seed=42
                            )

                            ga_instance.run()
                            solution, solution_fitness, _ = ga_instance.best_solution()
                            K_opt = solution

                            status_text.text(
                                f"GA completed: {num_generations} generations, cost = {-solution_fitness:.4f}")

                    progress_bar.progress(1.0)

                    controller_params = {f'K{i + 1}': K_opt[i] for i in range(n_states)}
                    st.session_state.designed_controller = controller_params
                    st.session_state.opt_history = opt_history
                    st.session_state.design_method = design_method

            # Persistent display for FSF design results
            if 'designed_controller' in st.session_state and st.session_state.controller_mode == "FSF":
                controller_params = st.session_state.designed_controller
                opt_history = st.session_state.get('opt_history', {})
                design_method = st.session_state.get('design_method', "Unknown")

                if design_method == "LQR (requires linearization)":
                    st.success("✅ LQR Controller Designed!")
                else:
                    st.success("✅ FSF Controller Designed!")
                st.write("**State Feedback Gains:**")
                cols = st.columns(min(n_states, 4))
                K_opt = [controller_params[f'K{i + 1}'] for i in range(n_states)]
                for i, k_val in enumerate(K_opt):
                    with cols[i % len(cols)]:
                        st.metric(f"K{i + 1}", f"{k_val:.4f}")

                # Visualization
                if opt_history and opt_history['iteration']:
                    st.subheader("Optimization Progress")

                    n_plots = n_states + 1
                    n_cols = min(3, n_plots)
                    n_rows = (n_plots + n_cols - 1) // n_cols

                    subplot_titles = ['Cost Function'] + [f'K{i + 1} Evolution' for i in range(n_states)]

                    fig_opt = make_subplots(
                        rows=n_rows, cols=n_cols,
                        subplot_titles=subplot_titles,
                        vertical_spacing=0.12,
                        horizontal_spacing=0.1
                    )

                    # Cost evolution
                    fig_opt.add_trace(
                        go.Scatter(x=opt_history['iteration'], y=opt_history['cost'],
                                   mode='lines+markers', name='Cost',
                                   line=dict(color='red', width=2)),
                        row=1, col=1
                    )

                    # K evolutions
                    colors = ['blue', 'green', 'orange', 'purple', 'brown', 'pink']
                    for i in range(n_states):
                        plot_idx = i + 2
                        row = (plot_idx - 1) // n_cols + 1
                        col = (plot_idx - 1) % n_cols + 1

                        fig_opt.add_trace(
                            go.Scatter(x=opt_history['iteration'], y=opt_history[f'K{i + 1}'],
                                       mode='lines+markers', name=f'K{i + 1}',
                                       line=dict(color=colors[i % len(colors)], width=2)),
                            row=row, col=col
                        )

                    # Update axes
                    for i in range(n_plots):
                        row = i // n_cols + 1
                        col = i % n_cols + 1
                        fig_opt.update_xaxes(title_text="Iteration", row=row, col=col)

                    fig_opt.update_layout(height=300 * n_rows, showlegend=False,
                                          title_text=f"{design_method} Progress")

                    st.plotly_chart(fig_opt, use_container_width=True)

        # Simulation section
        if 'designed_controller' in st.session_state:
            st.divider()
            st.subheader("Closed-Loop Simulation")

            num_runs = st.slider("Number of Monte Carlo runs", 1, 100, 20)

            if st.button("▶️ Run Simulation", type="primary"):
                with st.spinner(f"Running {num_runs} simulations..."):
                    controller_params = st.session_state.designed_controller

                    all_outputs = []
                    all_controls = []
                    all_metrics = []

                    sim_progress = st.progress(0)
                    for run_idx in range(num_runs):
                        result = simulator.evaluate_parameters(controller_params)
                        if result['success']:
                            all_outputs.append(result['trajectory'])
                            all_controls.append(result['control_signals'])
                            all_metrics.append(result['metrics'])
                        sim_progress.progress((run_idx + 1) / num_runs)

                    sim_progress.empty()

                    if not all_outputs:
                        st.error("All simulations failed!")
                    else:
                        # Process results
                        max_len = max(len(traj) for traj in all_outputs)
                        time_vec = np.arange(0, max_len * dt, dt)[:max_len]

                        # Create matrices for statistics
                        output_matrix = np.full((len(all_outputs), max_len), np.nan)
                        control_matrix = np.full((len(all_controls), max_len), np.nan)

                        for i, (out, ctrl) in enumerate(zip(all_outputs, all_controls)):
                            output_matrix[i, :len(out)] = out
                            control_matrix[i, :len(ctrl)] = ctrl

                        # Statistics
                        out_mean = np.nanmean(output_matrix, axis=0)
                        out_std = np.nanstd(output_matrix, axis=0)
                        ctrl_mean = np.nanmean(control_matrix, axis=0)
                        ctrl_std = np.nanstd(control_matrix, axis=0)

                        # Plot
                        fig = make_subplots(
                            rows=2, cols=1,
                            subplot_titles=['System Output (with ±1σ band)', 'Control Input (with ±1σ band)'],
                            vertical_spacing=0.12
                        )

                        # Output plot
                        fig.add_trace(
                            go.Scatter(x=time_vec, y=out_mean, mode='lines',
                                       name='Mean Output',
                                       line=dict(color='blue', width=2)),
                            row=1, col=1
                        )
                        fig.add_trace(
                            go.Scatter(x=time_vec, y=out_mean + out_std, mode='lines',
                                       name='Upper bound', line=dict(width=0),
                                       showlegend=False),
                            row=1, col=1
                        )
                        fig.add_trace(
                            go.Scatter(x=time_vec, y=out_mean - out_std, mode='lines',
                                       name='±1σ', fill='tonexty',
                                       line=dict(width=0),
                                       fillcolor='rgba(0,100,200,0.2)'),
                            row=1, col=1
                        )
                        fig.add_hline(y=target, line_dash="dash", line_color="green",
                                      row=1, col=1, annotation_text="Target")

                        # Control plot
                        fig.add_trace(
                            go.Scatter(x=time_vec, y=ctrl_mean, mode='lines',
                                       name='Mean Control',
                                       line=dict(color='orange', width=2)),
                            row=2, col=1
                        )
                        fig.add_trace(
                            go.Scatter(x=time_vec, y=ctrl_mean + ctrl_std, mode='lines',
                                       line=dict(width=0), showlegend=False),
                            row=2, col=1
                        )
                        fig.add_trace(
                            go.Scatter(x=time_vec, y=ctrl_mean - ctrl_std, mode='lines',
                                       fill='tonexty', name='±1σ',
                                       line=dict(width=0),
                                       fillcolor='rgba(255,140,0,0.2)'),
                            row=2, col=1
                        )

                        # Formatting
                        gains_str = ', '.join([f"{k}:{v:.3f}" for k, v in controller_params.items()])
                        fig.update_layout(
                            height=700,
                            title=f"Closed-Loop Response | {st.session_state.controller_mode} | {gains_str}",
                            showlegend=True
                        )
                        fig.update_xaxes(title_text="Time (s)", row=2, col=1)
                        fig.update_yaxes(title_text="Output", row=1, col=1)
                        fig.update_yaxes(title_text="Control", row=2, col=1)

                        st.plotly_chart(fig, use_container_width=True)

                        # Metrics
                        st.subheader("Performance Metrics (Mean ± Std)")
                        avg_metrics = {key: np.mean([m[key] for m in all_metrics])
                                       for key in all_metrics[0].keys()}
                        std_metrics = {key: np.std([m[key] for m in all_metrics])
                                       for key in all_metrics[0].keys()}

                        col_m1, col_m2, col_m3 = st.columns(3)
                        with col_m1:
                            st.metric("MSE", f"{avg_metrics['mse']:.4f} ± {std_metrics['mse']:.4f}")
                            st.metric("Settling Time",
                                      f"{avg_metrics['settling_time']:.2f}s ± {std_metrics['settling_time']:.2f}s")
                        with col_m2:
                            st.metric("Overshoot (%)",
                                      f"{avg_metrics['overshoot']:.2f} ± {std_metrics['overshoot']:.2f}")
                            st.metric("Steady-State Error",
                                      f"{avg_metrics['ss_error']:.4f} ± {std_metrics['ss_error']:.4f}")
                        with col_m3:
                            st.metric("Rise Time", f"{avg_metrics['rise_time']:.2f}s ± {std_metrics['rise_time']:.2f}s")
                            stable_pct = sum(1 for m in all_metrics if m['stable']) / len(all_metrics) * 100
                            st.metric("Stability", f"{stable_pct:.0f}% stable")

                        # Export controller
                        st.divider()
                        st.subheader("Export Controller")
                        export_format = st.radio("Export format:", ["Python dict", "JSON", "CSV"])

                        if export_format == "Python dict":
                            export_str = str(controller_params)
                        elif export_format == "JSON":
                            import json

                            export_str = json.dumps(controller_params, indent=2)
                        else:  # CSV
                            export_str = "Parameter,Value\n" + "\n".join(
                                [f"{k},{v}" for k, v in controller_params.items()])

                        st.code(export_str,
                                language="python" if export_format == "Python dict" else "json" if export_format == "JSON" else "csv")
                        st.download_button("📥 Download Controller", export_str,
                                           file_name=f"controller_{st.session_state.controller_mode}.txt")

    # Cleanup
    if 'dynamics_path' in st.session_state:
        try:
            os.unlink(st.session_state.dynamics_path)
            del st.session_state.dynamics_path
        except:
            pass
else:
    st.info("👆 Upload a dynamics file (.py or .m) to begin automated controller design")
    st.markdown("""
    ### Features:

    #### PID Controller Design
    - **Ziegler-Nichols**: Classic relay-based tuning
    - **Gradient-based Optimization**: L-BFGS-B method with visualization
    - **Genetic Algorithm (PyGAD)**: Global search with real-time progress tracking

    #### Full-State Feedback (FSF) Design
    - **LQR**: Optimal control via Riccati equation (requires linearization)
    - **Gradient-based Optimization**: Direct gain optimization with progress visualization
    - **Genetic Algorithm (PyGAD)**: Robust global optimization with generation tracking

    #### Evaluation
    - **Monte Carlo Simulation**: Test robustness across multiple initial conditions
    - **Comprehensive Metrics**: MSE, settling time, overshoot, steady-state error, stability
    - **Optimization Visualization**: Track cost function and parameter evolution
    - **Controller Export**: Save designed controllers in multiple formats

    #### New Features
    - **Real-time Progress Tracking**: Visualize optimization convergence
    - **PyGAD Integration**: Advanced genetic algorithm with customizable parameters
    - **Enhanced Control**: Support for MIMO systems with trim values and control limits
    - **Scenario Configuration**: Adjust noise, disturbances, and initial conditions
    """)