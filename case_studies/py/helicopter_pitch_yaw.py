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