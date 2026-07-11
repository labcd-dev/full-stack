function xdot = dynamics(t, x, u)
    mr = 0.095; mp = 0.024; Lr = 0.085; Lp = 0.129;
    Jr = 2e-4; Jp = 4e-5; Br = 5e-5; Bp = 1e-5; g = 9.81;
    
    theta = x(1); alpha = x(2); dtheta = x(3); dalpha = x(4);
    
    % Mass matrix elements
    M11 = Jr + mp*Lr^2;
    M12 = 0.25*mp*Lr*Lp*cos(alpha);
    M22 = Jp + 0.25*mp*Lp^2;
    
    % Nonlinear terms
    C1 = -0.25*mp*Lr*Lp*sin(alpha)*dalpha^2 - Br*dtheta;
    C2 = 0.125*mp*Lr*Lp*sin(alpha)*dtheta^2 - 0.5*mp*g*Lp*sin(alpha) - Bp*dalpha;
    
    % Solve for accelerations
    detM = M11*M22 - M12^2;
    ddtheta = (M22*(u + C1) - M12*C2) / detM;
    ddalpha = (M11*C2 - M12*(u + C1)) / detM;
    
    xdot = [dtheta; dalpha; ddtheta; ddalpha];
end