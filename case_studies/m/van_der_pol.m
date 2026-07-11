function xdot = dynamics(t, x, u)
    mu = 2.0;  % nonlinearity parameter
    x1 = x(1); x2 = x(2);
    xdot = [x2; mu*(1 - x1^2)*x2 - x1 + u];
end