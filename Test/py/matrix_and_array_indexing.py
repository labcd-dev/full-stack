from numpy import *
# Create a sample matrix a[10x10 for demonstration]
a = reshape(arange(1, 101), (10, 10), order='F')
b = arange(1, 102)
c = arange(1, 10 + 0.1, 0.1)
d = arange(1, 11)
z2d = zeros((3, 4))
z3d = zeros((3, 4, 5))
o2d = ones((3, 4))
identity = eye(3)
# Transpose
aTrans = a.transpose()
print(aTrans)
aConjTrans = a.conj().transpose()
print(aConjTrans)
col_vec = arange(1, 11)[:, newaxis]
# Display original matrix
print('Original matrix a:')
print(a)
# 1. Last element[linear indexing]
print('a[-1]:')

print(a[-1])
# 2. Element at row 2, column 5
print('a[1, 4]:')

print(a[1, 4])
# 3. First 5 rows, all columns
print('a[0:5, :]:')

print(a[0:5, :])
# 4. Last 5 rows, all columns
print('a[a.shape[0]-4:, :]:')

print(a[a.shape[0]-4:, :])
# 5. Specific rows array([2, 4, 5]) and columns array([1, 3])
print('a[ix_(array([1, 3, 4]), array([0, 2]))]:')

print(a[ix_(array([1, 3, 4]), array([0, 2]))])
# 6. Every other row from row 3 to row 21 (step 2)
print('a[2:21:2, :]:')

print(a[2:10:2, :])
# 7. Every other row from first row
print('a[0::2, :]:')

print(a[0::2, :])
# 8. Rows in reverse order
print('a[::-1, :]:')

print(a[::-1, :])
# 9. Append a copy of the first row to the end[corrected syntax]
print('a[r_[0:a.shape[0], 0], :]:')

print(a[r_[0:a.shape[0], 0], :])

# 10. Define matrix
a = array([1.02, 3.04, 5.06])
b = array([[1, 2, 3], [4, 5, 6]])
c = array([1.02, 3.04, 5.06])
d = array([[a], [c]])
e = array([a, c])
print(d)
print(e)