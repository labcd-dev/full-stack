function xdot = dynamics(t, x, u)
    m = 1; c = 0.5; ki = 0.001; g = 9.81;
    x1 = x(1); v1 = x(2); x2 = x(3); v2 = x(4);
    F1 = ki * u / ((x1+1)^2);
    F2 = ki * u / ((x2+1)^2);
    xdot = [v1; F1/m - c*v1/m - g; v2; F2/m - c*v2/m];
end