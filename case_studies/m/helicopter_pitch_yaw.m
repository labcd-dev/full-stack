function xdot = dynamics(t, x, u)
    Jp = 0.91; Jy = 1.3; Kpp = 0.2; Kyy = 0.3;
    Kpy = 0.01; Kyp = 0.01; g = 9.81; lp = 0.5; ly = 0.6;
    
    pitch = x(1); dpitch = x(2); yaw = x(3); dyaw = x(4);
    
    % Simplified helicopter dynamics
    Tp = lp * u;  % pitch torque
    Ty = ly * u * sin(pitch);  % yaw torque coupled through pitch
    
    xdot = [dpitch;
            (Tp - Kpp*dpitch - Kpy*dyaw - g*lp*sin(pitch)) / Jp;
            dyaw;
            (Ty - Kyy*dyaw - Kyp*dpitch) / Jy];
end