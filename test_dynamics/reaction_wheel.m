function xdot = dynamics(t, x, u)
    mp = 1; mw = 0.5; lp = 0.5; Ip = 0.1; Iw = 0.01;
    bp = 0.01; bw = 0.05; g = 9.81;
    
    theta = x(1); dtheta = x(2); phi = x(3); dphi = x(4);
    
    % Equations of motion with momentum exchange
    M = Ip + Iw + mp*lp^2;
    tau_p = -mp*g*lp*sin(theta) - bp*dtheta + u;
    tau_w = -u - bw*dphi;
    
    ddtheta = (tau_p - tau_w) / M;
    ddphi = tau_w / Iw - ddtheta;
    
    xdot = [dtheta; ddtheta; dphi; ddphi];
end