function xdot = dynamics(t, x, u)
    L = 0.001; C = 0.0001; R = 10; Vin = 12;
    iL = x(1); vC = x(2);
    D = max(0, min(1, u));  % duty cycle
    xdot = [(Vin - D*vC) / L;
            (D*iL - vC/R) / C];
end