function xdot = quadcopter_dynamics(t,x,omega)
X     = x(1);
Y     = x(2);
Z     = x(3);

u     = x(4);
v     = x(5);
w     = x(6);

phi   = x(7);
theta = x(8);
psi   = x(9);

p     = x(10);
q     = x(11);
r     = x(12);

m  = 1.5;
g  = 9.81;

Ix = 0.02;
Iy = 0.02;
Iz = 0.04;

l  = 0.25;      

kf = 1.2e-5;    
km = 2.4e-7;     

Cd = 0.1;     


w1 = omega(1);
w2 = omega(2);
w3 = omega(3);
w4 = omega(4);

F1 = kf*w1^2;
F2 = kf*w2^2;
F3 = kf*w3^2;
F4 = kf*w4^2;

T = F1 + F2 + F3 + F4;


tau_phi = l*(F2 - F4);

tau_theta = l*(F3 - F1);

tau_psi = km*( ...
     w1^2 ...
   - w2^2 ...
   + w3^2 ...
   - w4^2 );

tau = [tau_phi; tau_theta; tau_psi];

%% Rotation matrix

cphi = cos(phi);
sphi = sin(phi);

cth = cos(theta);
sth = sin(theta);

cps = cos(psi);
sps = sin(psi);

R = [...
cth*cps, ...
sphi*sth*cps-cphi*sps, ...
cphi*sth*cps+sphi*sps;

cth*sps, ...
sphi*sth*sps+cphi*cps, ...
cphi*sth*sps-sphi*cps;

-sth, ...
sphi*cth, ...
cphi*cth];

%% Position dynamics

vel_inertial = R*[u;v;w];

Xdot = vel_inertial(1);
Ydot = vel_inertial(2);
Zdot = vel_inertial(3);

Vb = [u;v;w];

omega_b = [p;q;r];

Fg_body = R'*[0;0;m*g];

Fthrust_body = [0;0;-T];

Fdrag = -Cd*Vb;

acc_body = ...
    (1/m)*(Fthrust_body + Fdrag + Fg_body) ...
    - cross(omega_b,Vb);

udot = acc_body(1);
vdot = acc_body(2);
wdot = acc_body(3);

%% Euler angle kinematics

E = [...
1, sin(phi)*tan(theta), cos(phi)*tan(theta);

0, cos(phi), -sin(phi);

0, sin(phi)/cos(theta), cos(phi)/cos(theta)];

eulerdot = E*omega_b;

phidot   = eulerdot(1);
thetadot = eulerdot(2);
psidot   = eulerdot(3);

%% Rotational dynamics

I = diag([Ix Iy Iz]);

omega_dot = I \ ...
    (tau - cross(omega_b,I*omega_b));

pdot = omega_dot(1);
qdot = omega_dot(2);
rdot = omega_dot(3);

%% Assemble state derivative

xdot = [...
    Xdot;
    Ydot;
    Zdot;
    udot;
    vdot;
    wdot;
    phidot;
    thetadot;
    psidot;
    pdot;
    qdot;
    rdot];
end