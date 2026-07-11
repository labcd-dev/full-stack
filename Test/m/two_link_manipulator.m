function xdot = dynamics(t, x, u)
    m1 = 1; m2 = 1; l1 = 1; l2 = 1; lc1 = 0.5; lc2 = 0.5;
    I1 = 0.083; I2 = 0.083; g = 9.81; b1 = 0.1; b2 = 0.1;
    
    q1 = x(1); q2 = x(2); dq1 = x(3); dq2 = x(4);
    
    % Inertia matrix
    M11 = m1*lc1^2 + m2*(l1^2 + lc2^2 + 2*l1*lc2*cos(q2)) + I1 + I2;
    M12 = m2*(lc2^2 + l1*lc2*cos(q2)) + I2;
    M22 = m2*lc2^2 + I2;
    
    % Coriolis, centrifugal, and gravity
    h = -m2*l1*lc2*sin(q2);
    C = [h*dq2*(2*dq1 + dq2); -h*dq1^2];
    G = [g*(m1*lc1 + m2*l1)*sin(q1) + g*m2*lc2*sin(q1+q2);
         g*m2*lc2*sin(q1+q2)];
    B = [b1*dq1; b2*dq2];
    
    % Accelerations
    tau = [u; 0];  % Only first joint actuated
    detM = M11*M22 - M12^2;
    ddq1 = (M22*(tau(1) - C(1) - G(1) - B(1)) - M12*(tau(2) - C(2) - G(2) - B(2))) / detM;
    ddq2 = (M11*(tau(2) - C(2) - G(2) - B(2)) - M12*(tau(1) - C(1) - G(1) - B(1))) / detM;
    
    xdot = [dq1; dq2; ddq1; ddq2];
end