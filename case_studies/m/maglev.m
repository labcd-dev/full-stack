function xdot = dynamics(t, x, u)
    m = 0.05; g = 9.81; L = 0.01; R = 1.0; k = 0.0001;
    z = x(1); v = x(2); i = x(3);
    F_mag = k * i^2 / (z^2 + 0.001);
    z_dot = v;
    v_dot = g - F_mag / m;
    i_dot = (u - R * i - k * i * v / (z^2 + 0.001)) / L;
    xdot = [z_dot; v_dot; i_dot];
end