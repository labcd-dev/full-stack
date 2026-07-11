function xdot = dynamics(t, x, u)
    A = 1.0; a1 = 0.1; a2 = 0.1; a3 = 0.1; g = 9.81;
    h1 = x(1); h2 = x(2); h3 = x(3);
    xdot = [u/A - a1/A * sqrt(2*g*h1);
            a1/A * sqrt(2*g*h1) - a2/A * sqrt(2*g*h2);
            a2/A * sqrt(2*g*h2) - a3/A * sqrt(2*g*h3)];
end