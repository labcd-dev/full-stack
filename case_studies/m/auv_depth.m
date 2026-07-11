function xdot = dynamics(t, x, u)
    m = 50; Iz = 5; W = 500; B = 510; zb = -0.1; zg = 0;
    Zw = -20; Zq = -5; Zd = -10; Mw = -3; Mq = -8; Md = -5;
    z = x(1); w = x(2); theta = x(3); q = x(4);
    xdot = [w*cos(theta) - sin(theta);
            (Zw*w + Zq*q + Zd*u + (W-B)*sin(theta)) / m;
            q;
            (Mw*w + Mq*q + Md*u + (zg*W - zb*B)*sin(theta)) / Iz];
end