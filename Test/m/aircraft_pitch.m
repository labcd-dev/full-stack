function xdot = dynamics(t, x, u)
    % Aircraft longitudinal (pitch) dynamics
    % States: [pitch_angle; pitch_rate; vertical_velocity]
    % Input: elevator_deflection
    
    % Aircraft parameters
    m = 1000;      % mass (kg)
    Iy = 3000;     % pitch moment of inertia (kg*m^2)
    S = 16;        % wing area (m^2)
    c = 1.5;       % mean aerodynamic chord (m)
    rho = 1.225;   % air density (kg/m^3)
    V = 50;        % airspeed (m/s)
    
    % Aerodynamic coefficients
    CL_alpha = 4.5;
    CM_alpha = -0.8;
    CM_q = -15;
    CM_delta = -1.2;
    
    theta = x(1);      % pitch angle
    q = x(2);          % pitch rate
    w = x(3);          % vertical velocity
    
    alpha = atan(w / V);  % angle of attack
    Q = 0.5 * rho * V^2;  % dynamic pressure
    
    % Aerodynamic forces and moments
    L = Q * S * CL_alpha * alpha;
    M = Q * S * c * (CM_alpha * alpha + CM_q * q * c / (2*V) + CM_delta * u);
    
    % State derivatives
    theta_dot = q;
    q_dot = M / Iy;
    w_dot = (L * cos(theta) - m * 9.81 * sin(theta)) / m - V * q;
    
    xdot = [theta_dot; q_dot; w_dot];
end