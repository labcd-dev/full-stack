import os
import tempfile
import numpy as np
from ga_utils import GAOptimizer

# ============================================================================
# CONFIGURATION
# ============================================================================

# LLM Model (not used in GA, but kept for consistency)
# llm_model = "qwen-3-32b"

# System Configuration
system_name = "ball_beam"  # Options: "dc_motor", "ball_beam", "inverted_pendulum", "double_pendulum", "custom"

# For custom systems
file_type = "Python (.py)"  # "Python (.py)" or "MATLAB/Octave (.m)"
dynamics_code = """
import numpy as np

def dynamics(t, x, u):
    # Example: Simple 2-state system
    # x' = [x2; -0.5*x1 - 0.3*x2 + u]
    xdot = np.zeros(2)
    xdot[0] = x[1]
    xdot[1] = -0.5*x[0] - 0.3*x[1] + u[0]
    return xdot
"""
matlab_func_name = None  # Required for MATLAB files
num_states = None  # Auto-detect if None

# Simulation Parameters
dt = 0.01
max_time = 5.0
target = 0.0  # Upright position for inverted pendulum
num_inputs = 1
input_channel = 0
output_channel = 0
trim_values = None
min_ctrl = -10.0
max_ctrl = 10.0

# Controller Type Selection
controller_type = "LQR"  # Options: "PID", "FSF", "LQR"

# GA Parameters
ga_config = {
    "num_generations": 100,
    "population_size": 50,
    "num_parents_mating": 10,
    "keep_parents": 2,
    "crossover_probability": 0.8,
    "mutation_probability": 0.1,
    "mutation_num_genes": 1,
    "random_seed": 42
}

# Controller Parameter Ranges
param_ranges = {
    "PID": {
        "Kp": [1.0, 100.0],
        "Ki": [0.01, 20.0],
        "Kd": [0.01, 50.0]
    },
    "FSF": {
        # Will be auto-generated based on num_states
        # Example for 2-state: {"K1": [0.1, 50.0], "K2": [0.1, 50.0]}
    },
    "LQR": {
        # Diagonal Q matrix elements
        "Q_diag": [[0.1, 100.0]] * 2,  # Will be adjusted based on num_states
        # R matrix (scalar for SISO)
        "R": [0.01, 10.0]
    }
}

# Scenario Configuration
scenario_config = {
    "initial_condition_range": [1, 1],  #[np.pi - 0.1*np.pi, np.pi + 0.1*np.pi],  # Near upright
    "randomness_level": 0.0,
    "disturbance_level": 0.0,
    "param_uncertainty": 0.0
}

# Evaluation Parameters
num_evaluation_runs = 10  # Monte Carlo runs for fitness evaluation

# Optimization Weights
weights = {
    "mse": 1.0,
    "settling_time": 0.1,
    "overshoot": 0.01,
    "control_effort": 0.001
}

# ============================================================================
# MAIN EXECUTION
# ============================================================================

if __name__ == "__main__":
    # Handle custom dynamics
    custom_dynamics_path = None
    if system_name == "custom":
        if not dynamics_code.strip():
            raise ValueError("dynamics_code must be provided for custom systems")
        suffix = ".py" if file_type == "Python (.py)" else ".m"
        with tempfile.NamedTemporaryFile(suffix=suffix, delete=False, mode='w') as tmp:
            tmp.write(dynamics_code)
            custom_dynamics_path = tmp.name
        if file_type == "MATLAB/Octave (.m)" and not matlab_func_name:
            raise ValueError("matlab_func_name required for MATLAB/Octave files")

    # Create optimizer
    optimizer = GAOptimizer(
        system_name=system_name,
        controller_type=controller_type,
        ga_config=ga_config,
        param_ranges=param_ranges,
        scenario_config=scenario_config,
        num_evaluation_runs=num_evaluation_runs,
        weights=weights,
        custom_dynamics_path=custom_dynamics_path,
        file_type=file_type,
        matlab_func_name=matlab_func_name,
        num_states=num_states,
        dt=dt,
        max_time=max_time,
        target=target,
        num_inputs=num_inputs,
        input_channel=input_channel,
        output_channel=output_channel,
        trim_values=trim_values,
        min_ctrl=min_ctrl,
        max_ctrl=max_ctrl
    )

    # Run optimization
    print(f"\n{'='*70}")
    print(f"GA-Based Controller Optimization")
    print(f"{'='*70}")
    print(f"System: {system_name}")
    print(f"Controller Type: {controller_type}")
    print(f"Population Size: {ga_config['population_size']}")
    print(f"Generations: {ga_config['num_generations']}")
    print(f"{'='*70}\n")

    best_params, best_fitness, history = optimizer.optimize()

    # Display results
    print(f"\n{'='*70}")
    print(f"OPTIMIZATION COMPLETE")
    print(f"{'='*70}")
    print(f"Best Fitness (Cost): {-best_fitness:.6f}")
    print(f"\nOptimal Parameters:")
    for param, value in best_params.items():
        print(f"  {param}: {value:.6f}")
    print(f"{'='*70}\n")

    # Visualize results
    optimizer.plot_optimization_history(history)
    optimizer.plot_time_response(best_params, num_runs=50)

    # Cleanup
    if custom_dynamics_path:
        os.unlink(custom_dynamics_path)

    print("\nOptimization complete! Check generated plots.")