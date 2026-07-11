function xdot = dynamics(t, x, u)
    A1 = 0.5; A2 = 0.5; A3 = 0.5; A4 = 0.5;
    a1 = 0.05; a2 = 0.05; a3 = 0.05; a4 = 0.05;
    g = 9.81; gamma1 = 0.4; gamma2 = 0.4;
    h1 = x(1); h2 = x(2); h3 = x(3); h4 = x(4);
    xdot = [-a1/A1*sqrt(2*g*h1) + a3/A1*sqrt(2*g*h3) + gamma1/A1*u;
            -a2/A2*sqrt(2*g*h2) + a4/A2*sqrt(2*g*h4) + gamma2/A2*u;
            -a3/A3*sqrt(2*g*h3) + (1-gamma2)/A3*u;
            -a4/A4*sqrt(2*g*h4) + (1-gamma1)/A4*u];
end