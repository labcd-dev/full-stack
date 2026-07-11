from numpy import *

def matrix_operations(a, b, M):
    # horiz_cat = concatenate((a, b), 1)
    # vert_cat = concatenate((a, b))
    sorted_cols = sort(a)
    sorted_rows = sort(a, axis=1)
    I = argsort(a[:, 0])
    sorted_rows_array = a[I, :]
    unsqueezed = a.squeeze()
    row = M[1, :]
    corner = M[-1, -1]
    return horiz_cat, vert_cat, sorted_cols, sorted_rows, sorted_rows_array, I, unsqueezed, row, corner