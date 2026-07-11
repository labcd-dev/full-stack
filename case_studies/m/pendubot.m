function xdot = dynamics(t, x, u)
    m1 = 1; m2 = 1; l1 = 1; l2 = 1; lc1 = 0.5; lc2 = 0.5;
    I1 = 0.1; I2 = 0.1; g = 9.81;
    q1 = x(1); dq1 = x(2); q2 = x(3); dq2 = x(4);
    
    % Mass matrix
    M11 = m1*lc1^2 + m2*(l1^2 + lc2^2 + 2*l1*lc2*cos(q2)) + I1 + I2;
    M12 = m2*(lc2^2 + l1*lc2*cos(q2)) + I2;
    M22 = m2*lc2^2 + I2;
    
    % Coriolis and gravity terms
    h = -m2*l1*lc2*sin(q2);
    C1 = h*dq2^2 + 2*h*dq1*dq2;
    C2 = -h*dq1^2;
    G1 = (m1*lc1 + m2*l1)*g*sin(q1) + m2*lc2*g*sin(q1+q2);
    G2 = m2*lc2*g*sin(q1+q2);
    
    % Solve for accelerations
    detM = M11*M22 - M12^2;
    ddq1 = (M22*(u - C1 - G1) - M12*(-C2 - G2)) / detM;
    ddq2 = (M11*(-C2 - G2) - M12*(u - C1 - G1)) / detM;
    
    xdot = [dq1; ddq1; dq2; ddq2];
end