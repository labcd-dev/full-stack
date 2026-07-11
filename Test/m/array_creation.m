function [z2d, z3d, o2d, identity, diag_vec, diag_mat, rand_mat, grid_line, x1, y1, x2, y2, repeated] = array_creation(a, v)
    z2d = zeros(3,4);
    z3d = zeros(3,4,5);
    o2d = ones(3,4);
    identity = eye(3);
    diag_vec = diag(a);
    diag_mat = diag(v,0);
    rng(42,'twister');
    rand_mat = rand(3,4);
    grid_line = linspace(1,3,4);
    [x1, y1] = meshgrid(0:8,0:5);
    [x2, y2] = meshgrid([1,2,4],[2,4,5]);
    repeated = repmat(a, 2, 3);
end