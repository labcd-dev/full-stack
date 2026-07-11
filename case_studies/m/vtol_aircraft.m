function xdot = dynamics(t, x, u)
    m = 4; g = 9.81; Jx = 0.2; Jy = 0.3; Jz = 0.4;
    x_pos = x(1); vx = x(2); phi = x(3); p = x(4); theta = x(5); q = x(6);
    T = 45; % thrust
    xdot = [vx;
            (T*sin(theta) - 0.1*vx) / m;
            p;
            u / Jx;
            q;
            (-T*sin(phi)*cos(theta) - 0.05*q) / Jy];
end