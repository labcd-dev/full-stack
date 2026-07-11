function quadcopter_sim()
    % Clear workspace and command window
    clear; clc; close all;

    %% 1. Simulation Parameters
    t_span = [0 10]; % Simulation time from 0 to 10 seconds

    % Initial State Vector: [x; y; z; phi; theta; psi; u; v; w; p; q; r]
    % Position: (0, 0, 0)
    % Orientation: Roll=0.1 rad, Pitch=-0.1 rad, Yaw=0.2 rad (Initial tilt to test stabilization)
    % Velocities: All 0
    X0 = [0; 0; 0; 0.1; -0.1; 0.2; 0; 0; 0; 0; 0; 0];

    %% 2. Run Simulation using ODE45
    [t, X] = ode45(@quadcopter_dynamics, t_span, X0);

    %% 3. Plot Results
    figure('Position', [100, 100, 1000, 600]);

    % Plot Position
    subplot(2,2,1);
    plot(t, X(:,1), 'r', t, X(:,2), 'g', t, X(:,3), 'b', 'LineWidth', 1.5);
    title('Position vs Time');
    xlabel('Time (s)'); ylabel('Position (m)');
    legend('X', 'Y', 'Z (Altitude)');
    grid on;

    % Plot Attitude (Angles)
    subplot(2,2,2);
    plot(t, rad2deg(X(:,4)), 'r', t, rad2deg(X(:,5)), 'g', t, rad2deg(X(:,6)), 'b', 'LineWidth', 1.5);
    title('Attitude vs Time');
    xlabel('Time (s)'); ylabel('Angle (deg)');
    legend('\phi (Roll)', '\theta (Pitch)', '\psi (Yaw)');
    grid on;

    % Plot Linear Velocities
    subplot(2,2,3);
    plot(t, X(:,7), 'r', t, X(:,8), 'g', t, X(:,9), 'b', 'LineWidth', 1.5);
    title('Linear Velocities vs Time');
    xlabel('Time (s)'); ylabel('Velocity (m/s)');
    legend('u (Forward)', 'v (Lateral)', 'w (Vertical)');
    grid on;

    % Plot Angular Velocities
    subplot(2,2,4);
    plot(t, rad2deg(X(:,10)), 'r', t, rad2deg(X(:,11)), 'g', t, rad2deg(X(:,12)), 'b', 'LineWidth', 1.5);
    title('Angular Velocities vs Time');
    xlabel('Time (s)'); ylabel('Rate (deg/s)');
    legend('p (Roll rate)', 'q (Pitch rate)', 'r (Yaw rate)');
    grid on;
end

%% 4. Quadcopter Dynamics & Control Function
function dXdt = quadcopter_dynamics(t, X)
    %% Physical Constants & Parameters
    g = 9.81;    % Gravity (m/s^2)
    m = 1.0;     % Mass (kg)
    L = 0.25;    % Arm length (m)
    k = 3e-6;    % Lift coefficient
    b = 1e-7;    % Drag coefficient

    % Moments of Inertia (kg*m^2)
    Ixx = 8.1e-3;
    Iyy = 8.1e-3;
    Izz = 14.2e-3;

    %% Extract States
    % Position/Orientation
    % x = X(1); y = X(2); z = X(3);
    phi = X(4); theta = X(5); psi = X(6);

    % Linear/Angular Velocities (Body Frame)
    u = X(7);  v = X(8);  w = X(9);
    p = X(10); q = X(11); r = X(12);

    %% 5. Controller (PD Control to Hover at Target)
    % Targets
    z_target = 2.0; % Hover at 2 meters
    phi_target = 0; theta_target = 0; psi_target = 0;

    % Gains
    Kp_z = 15;  Kd_z = 10;   % Altitude gains
    Kp_att = 4; Kd_att = 1;  % Attitude gains

    % Control Inputs (Desired Forces/Torques)
    % U1: Total Thrust, U2: Roll Torque, U3: Pitch Torque, U4: Yaw Torque
    U1 = m * g + Kp_z * (z_target - X(3)) - Kd_z * w;
    U2 = Kp_att * (phi_target - phi) - Kd_att * p;
    U3 = Kp_att * (theta_target - theta) - Kd_att * q;
    U4 = Kp_att * (psi_target - psi) - Kd_att * r;

    % Bound thrust to prevent negative/unrealistic values
    U1 = max(0, U1);

    %% 6. Equations of Motion (Newton-Euler)

    % Trigonometric shorthands
    s_ph = sin(phi);   c_ph = cos(phi);
    s_th = sin(theta); c_th = cos(theta);
    s_ps = sin(psi);   c_ps = cos(psi);

    % Rotation Matrix: Body Frame to Inertial Frame (R_ZYX)
    R = [c_th*c_ps, s_ph*s_th*c_ps - c_ph*s_ps, c_ph*s_th*c_ps + s_ph*s_ps;
         c_th*s_ps, s_ph*s_th*s_ps + c_ph*c_ps, c_ph*s_th*s_ps - s_ph*c_ps;
         -s_th,     s_ph*c_th,                 c_ph*c_th];

    % --- Linear Accelerations (Inertial Frame) ---
    % Gravity vector in inertial frame
    G = [0; 0; -g];
    % Thrust vector in body frame pointing upwards along Z-axis
    Thrust_B = [0; 0; U1];

    % Acceleration: F = m*a -> a = G + (R * Thrust_B)/m
    accel = G + (R * Thrust_B) / m;

    % --- Angular Accelerations (Body Frame) ---
    % p_dot, q_dot, r_dot equations including gyroscopic coupled terms
    p_dot = (U2 + (Iyy - Izz) * q * r) / Ixx;
    q_dot = (U3 + (Izz - Ixx) * p * r) / Iyy;
    r_dot = (U4 + (Ixx - Iyy) * p * q) / Izz;

    % --- Kinematics (Mapping body angular rates to Euler angle rates) ---
    % Note: Singular if theta = pi/2 (90 degrees)
    phi_dot   = p + q * s_ph * tan(theta) + r * c_ph * tan(theta);
    theta_dot = q * c_ph - r * s_ph;
    psi_dot   = q * s_ph / c_th + r * c_ph / c_th;

    %% 7. Assemble State Derivative Vector (dXdt)
    dXdt = zeros(12, 1);

    % Position rates (Inertial Frame velocities)
    % For simplicity in mapping states directly to output, we integrate
    % the inertial accelerations directly through the state updates.
    dXdt(1) = R(1,:)*[u;v;w]; % dx/dt
    dXdt(2) = R(2,:)*[u;v;w]; % dy/dt
    dXdt(3) = R(3,:)*[u;v;w]; % dz/dt

    % Attitude rates
    dXdt(4) = phi_dot;
    dXdt(5) = theta_dot;
    dXdt(6) = psi_dot;

    % Accelerations (Stored as body-frame state modifications)
    % Alternatively, maps directly back to the frame updates
    dXdt(7)  = accel(1);
    dXdt(8)  = accel(2);
    dXdt(9)  = accel(3);
    dXdt(10) = p_dot;
    dXdt(11) = q_dot;
    dXdt(12) = r_dot;
end