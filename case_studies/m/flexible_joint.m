function xdot = dynamics(t, x, u)
    J1 = 0.01; J2 = 0.01; k = 1.0; d = 0.1; b1 = 0.05; b2 = 0.05;
    theta1 = x(1); omega1 = x(2); theta2 = x(3); omega2 = x(4);
    xdot = [omega1;
            (u - k*(theta1 - theta2) - d*(omega1 - omega2) - b1*omega1) / J1;
            omega2;
            (k*(theta1 - theta2) + d*(omega1 - omega2) - b2*omega2) / J2];
end