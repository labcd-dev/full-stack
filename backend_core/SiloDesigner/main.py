import os
from backend_core.SiloDesigner.src.controllers import run_optimization
import tempfile

# CONFIGURATION
# Modify the settings below as needed
llm_model = "llama3.1-8b"  # Options: "llama-3.1-8b-instant", "qwen-3-32b", "gpt-oss-120b",
# "llama-3.3-70b", "deepseek-r1-distill-llama-70b", "gpt-4o", "gpt-4o-mini"
system_name = "custom"#"ball_beam"  # Options: "dc_motor", "ball_beam", "inverted_pendulum", "double_pendulum", "custom"

# If system_name == "custom", provide the following:
# file_type = "MATLAB/Octave (.m)"  # "Python (.py)" or "MATLAB/Octave (.m)"
# dynamics_code = """
# function xdot = dynamics(t, x, u)
#     %% Nonlinear system dynamics for 2-DOF pitch-yaw system
#     m = 1.3872;
#     g = 9.81;  % Gravitational acceleration
#     B_p = 0.8;  % Pitch viscous damping
#     B_y = 0.318;  % Yaw viscous damping
#     K_pp = 0.2040;  % Pitch torque gain from front motor
#     K_yy = 0.0720;  % Yaw torque gain from rear motor
#     K_py = 0.0068;  % Cross-coupling pitch torque gain from rear motor
#     K_yp = 0.0219;  % Cross-coupling yaw torque gain from front motor
#     J_p = 0.0178;  % Pitch moment of inertia about pivot
#     J_y = 0.0084;  % Yaw moment of inertia about pivot
#     l_cm = 0.186;  % Distance from pivot to center of mass
#     J_Tp = J_p + m * l_cm^2;  % Total pitch moment of inertia
#     J_Ty = J_y + m * l_cm^2;  % Total yaw moment of inertia
#
#     % State variables
#     pitch = x(1); yaw = x(2); dpitch = x(3); dyaw = x(4);
#
#     % Inputs: u = [u1; u2] (e.g., front and rear motor voltages/commands)
#     u1 = u(1); u2 = u(2);
#
#     % Motor torques (linear in inputs, with cross-coupling)
#     Tp = K_pp * u1 + K_py * u2;
#     Ty = K_yp * u1 + K_yy * u2;
#
#     % State derivatives
#     xdot = zeros(4, 1);
#     xdot(1) = dpitch;  % dot{pitch}
#     xdot(2) = dyaw;    % dot{yaw}
#     xdot(3) = (Tp - B_p * dpitch - m * g * l_cm * sin(pitch)) / J_Tp;  % ddot{pitch}
#     xdot(4) = (Ty - B_y * dyaw) / J_Ty;  % ddot{yaw}
# end
# """
# matlab_func_name = "dynamics" # None  # Required if file_type == "MATLAB/Octave (.m)", e.g., "dynamics"

file_type = "Python (.py)"  # "Python (.py)" or "MATLAB/Octave (.m)"
dynamics_code = """
import numpy as np

def dynamics(t, x, u):
    # Nonlinear system dynamics for 2-DOF pitch-yaw system
    m = 1.3872
    g = 9.81  # Gravitational acceleration
    B_p = 0.8  # Pitch viscous damping
    B_y = 0.318  # Yaw viscous damping
    K_pp = 0.2040  # Pitch torque gain from front motor
    K_yy = 0.0720  # Yaw torque gain from rear motor
    K_py = 0.0068  # Cross-coupling pitch torque gain from rear motor
    K_yp = 0.0219  # Cross-coupling yaw torque gain from front motor
    J_p = 0.0178  # Pitch moment of inertia about pivot
    J_y = 0.0084  # Yaw moment of inertia about pivot
    l_cm = 0.186  # Distance from pivot to center of mass
    J_Tp = J_p + m * l_cm**2  # Total pitch moment of inertia
    J_Ty = J_y + m * l_cm**2  # Total yaw moment of inertia

    # State variables
    pitch = x[0]
    yaw = x[1]
    dpitch = x[2]
    dyaw = x[3]

    # Inputs: u = [u1, u2] (e.g., front and rear motor voltages/commands)
    u1 = u[0]
    u2 = u[1]

    # Motor torques (linear in inputs, with cross-coupling)
    Tp = K_pp * u1 + K_py * u2
    Ty = K_yp * u1 + K_yy * u2

    # State derivatives
    xdot = np.zeros(4)
    xdot[0] = dpitch  # dot{pitch}
    xdot[1] = dyaw    # dot{yaw}
    xdot[2] = (Tp - B_p * dpitch - m * g * l_cm * np.sin(pitch)) / J_Tp  # ddot{pitch}
    xdot[3] = (Ty - B_y * dyaw) / J_Ty  # ddot{yaw}
    return xdot
"""
matlab_func_name = None
num_states = 4 # None # Optional integer; if None, will auto-detect for custom systems

# Simulation and Control Configuration
dt = 0.01  # Sample time
max_time = 5.0  # Simulation max time
target = 0.0  # Desired value for the output channel (can be scalar or function)
num_inputs = 2  # Number of system inputs (for MIMO support)
input_channel = 0  # Index of the input channel to control (0-based)
output_channel = 0  # Index of the output channel for metrics (0-based)
trim_values = None  # Trim values for other inputs (None defaults to zeros)
# Example: trim_values = [0.0, 1.5, 0.0] for a 3-input system

# Control limits
min_ctrl = -10.0  # Minimum control input limit
max_ctrl = 10.0   # Maximum control input limit

control_objective = "Design a stable controller with minimal settling time, overshoot, and steady-state error."
max_tries = 2  # Max tries for LLM Juror
controllers = ["PID"]  # List of controllers: ["P", "PI", "PD", "PID", "FSF"]
max_scenarios = 1
max_iter = 10
run_id = 1
seed = 42
custom_scenarios = [
    {
        "id": "I",
        "initial_condition_range": [1.0, 1.0],
        "randomness_level": 0,
        "disturbance_level": 0,
        "param_uncertainty": 0,
    }
    # },
    # {
    #     "id": "II",
    #     "initial_condition_range": [1.0, 1.5],
    #     "randomness_level": 0.01,
    #     "disturbance_level": 0.5,
    #     "param_uncertainty": 0.1,
    # }
]
target_metrics = {
    "mse": 0.18,
    "settling_time": 2.0,
    "overshoot": 5.0
    # Removed "max_iterations": nn to avoid duplication with max_iter
}

# Custom param_ranges (optional; if None, defaults will be used based on system num_states)
# For FSF, it will be generalized to {f"K{i+1}": [min, max] for i in range(num_states)}
# Leave as None to use system defaults
# custom_param_ranges = None
# Example:
custom_param_ranges = {
    "P": {"Kp": [60.0, 90.0]},
    "PI": {"Kp": [5.0, 50.0], "Ki": [0.01, 3.0]},
    "PD": {"Kp": [5.0, 50.0], "Kd": [0.01, 3.0]},
    "PID": {"Kp": [5.0, 50.0], "Ki": [0.01, 3.0], "Kd": [0.01, 10.0]},
    "FSF": {}  # Will be populated based on num_states if FSF is selected
}

# END OF CONFIGURATION

# Core code below handles the rest
custom_dynamics_path = None
if system_name == "custom":
    if not dynamics_code.strip():
        raise ValueError("dynamics_code must be provided for custom systems")
    suffix = ".py" if file_type == "Python (.py)" else ".m"
    with tempfile.NamedTemporaryFile(suffix=suffix, delete=False) as tmp:
        tmp.write(dynamics_code.encode())
        custom_dynamics_path = tmp.name
    if file_type == "MATLAB/Octave (.m)" and not matlab_func_name:
        raise ValueError("matlab_func_name required for MATLAB/Octave files")

# If custom_param_ranges provided and FSF selected, generalize FSF ranges if needed
if custom_param_ranges and "FSF" in controllers:
    # Use provided num_states if available; otherwise, create system temporarily to detect
    effective_num_states = num_states if num_states is not None else 0
    if effective_num_states == 0:
        from src.systems import create_system
        temp_system = create_system(
            system_name,
            custom_dynamics_path=custom_dynamics_path,
            file_type=file_type,
            matlab_func_name=matlab_func_name,
            num_states=num_states  # Still passed, but ignored in detection for custom Python
        )
        effective_num_states = temp_system.num_states
        if num_states is None:
            num_states = effective_num_states
    if not custom_param_ranges["FSF"]:
        # Default ranges for FSF based on (detected or provided) num_states
        custom_param_ranges["FSF"] = {f"K{i+1}": [0.01, 50.0] for i in range(effective_num_states)}

run_optimization(
    llm_model=llm_model,
    run_id=run_id,
    seed=seed,
    system_name=system_name,
    max_scenarios=max_scenarios,
    max_iter=max_iter,
    controllers=controllers,
    custom_scenarios=custom_scenarios,
    param_ranges=custom_param_ranges,
    target_metrics=target_metrics,
    custom_dynamics_path=custom_dynamics_path,
    file_type=file_type,
    matlab_func_name=matlab_func_name,
    num_states=num_states,
    max_tries=max_tries,
    control_objective=control_objective,
    dt=dt,
    max_time=max_time,
    target=target,
    num_inputs=num_inputs,
    input_channel=input_channel,
    output_channel=output_channel,
    trim_values=trim_values,
    min_ctrl=min_ctrl,    # NEW
    max_ctrl=max_ctrl     # NEW
)

# Cleanup temp file
if custom_dynamics_path:
    os.unlink(custom_dynamics_path)