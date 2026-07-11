from numpy import *
import scipy.linalg as linalg

def math_reductions(a, b, v):
    # max_global = a.max()
    # max_col = a.max(0)
    # max_row = a.max(1)
    # max_elem_wise = maximum(a, b)
    vector_norm = linalg.norm(v)
    log_and = logical_and(a, b)
    log_or = logical_or(a, b)
    bit_and = a & b
    bit_or = a | b
    return vector_norm, log_and, log_or, bit_and, bit_or