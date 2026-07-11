from numpy import *

def array_creation(a, v):
    z2d = zeros((3, 4))
    z3d = zeros((3, 4, 5))
    o2d = ones((3, 4))
    identity = eye(3)
    diag_vec = diag(a)
    diag_mat = diag(v, 0)
    rng = random.default_rng(42)
    rand_mat = rng.random((3, 4))
    grid_line = linspace(1, 3, 4)
    x1, y1 = meshgrid(r_[0:9.], r_[0:6.])
    x2, y2 = meshgrid([1, 2, 4], [2, 4, 5])
    repeated = tile(a, (2, 3))
    return z2d, z3d, o2d, identity, diag_vec, diag_mat, rand_mat, grid_line, x1, y1, x2, y2, repeated