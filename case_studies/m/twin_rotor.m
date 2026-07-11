function dxdt = trms_dynamics(t, x, u)
    % =========================================================================
    % TWIN ROTOR MIMO SYSTEM (TRMS) PLANT MODEL
    % Target: MATLAB ode45 / State-Space Simulation
    % =========================================================================

    %% 1. PARAMETERS (Physical Constants)
    J_vertical = 0.05;   % Moment of inertia around pitch axis [kg*m^2]
    J_horizontal = 0.04; % Moment of inertia around yaw axis [kg*m^2]

    % Aerodynamic force coefficients for rotors
    a1 = 0.012;          % Main rotor lift coefficient
    a2 = 0.010;          % Tail rotor thrust coefficient

    % Friction and damping constants
    B_pitch = 0.01;      % Viscous friction coefficient for pitch
    B_yaw = 0.015;       % Viscous friction coefficient for yaw

    % Gravity configuration
    MgL = 0.3;           % Gravitational momentum parameter [N*m]

    % Cross-coupling factor
    K_gyroscopic = 0.005; % Gyroscopic cross-coupling torque coefficient

    %% 2. UNPACK STATES & INPUTS
    % States:
    % x(1) = theta  (Pitch angle, rad)
    % x(2) = dtheta (Pitch angular velocity, rad/s)
    % x(3) = psi    (Yaw angle, rad)
    % x(4) = dpsi   (Yaw angular velocity, rad/s)
    theta  = x(1);
    dtheta = x(2);
    psi    = x(3);
    dpsi   = x(4);

    % Inputs:
    % u(1) = U_main (Control voltage/PWM to main motor)
    % u(2) = U_tail (Control voltage/PWM to tail motor)
    U_main = u(1);
    U_tail = u(2);

    %% 3. DYNAMICS / EQUATIONS OF MOTION
    % Main thrust forces (simplified as proportional to input voltage)
    Tau_main = a1 * U_main;
    Tau_tail = a2 * U_tail;

    % Pitch Axis Dynamics (Elevation)
    % Torque balances: Thrust - Gravity - Friction
    ddtheta = (Tau_main - MgL * cos(theta) - B_pitch * dtheta) / J_vertical;

    % Yaw Axis Dynamics (Azimuth)
    % Torque balances: Thrust - Friction + Cross-coupling interaction from main rotor
    Tau_cross = K_gyroscopic * Tau_main * dtheta; % Coupling effect
    ddpsi = (Tau_tail - B_yaw * dpsi + Tau_cross) / J_horizontal;

    %% 4. DERIVATIVE VECTOR CONSTRUCTION
    dxdt = zeros(4,1);
    dxdt(1) = dtheta;  % d(theta)/dt
    dxdt(2) = ddtheta; % d^2(theta)/dt^2
    dxdt(3) = dpsi;    % d(psi)/dt
    dxdt(4) = ddpsi;   % d^2(psi)/dt^2
end