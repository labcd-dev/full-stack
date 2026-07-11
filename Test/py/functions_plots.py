from numpy import *
import matplotlib.pyplot as plt
# =========================================================================
# MATLAB Test File for Translation Application
# =========================================================================
# =========================================================================
# Local Function Definitions
# =========================================================================
def compute_metrics(val1, val2):
    if val1 > val2:
        out1 = val1

        out2 = val2

    elif val1 == val2:
        out1 = 0

        out2 = 0

    else:
        out1 = val2

        out2 = val1

    return out1, out2
## 1. Matrix literals and Concatenation
# Testing 1D vectors and multi-dimensional matrices
a = array([1.02, 3.04, 5.06])

b = array([[1, 2, 3], [4, 5, 6]])

c = array([1.02, 3.04, 5.06])
# Testing horizontal and vertical concatenation of variables
d = array([[a], [c]])

e = array([a, c])

print('Matrix d:')
print(d)
print('Matrix e:')
print(e)
## 2. Basic Math and Syntax Rounding
print(f'Rounded array a:')
print(round(a))
## 3. Conditional Blocks and Custom Functions
# This section tests function scoping, indentation, and elif conversion
x_val, y_val = compute_metrics(10, 20)

x_zero, y_zero = compute_metrics(5, 5)
## 4. Loops and Iterative Execution
# Testing for loops, step index limits, and nested while loops
for i in range(1, 4):
    while i < 2:
        print('Nested execution active')
        i = i + 2

# Python while loop example
counter = 1
total = 0

while counter <= 5:
    total = total + counter
    print(f"Iteration {counter}: Sum = {total}")
    counter = counter + 1

print(f"Final total: {total}")

## 5. Visualization Rules
# Basic grid and plotting functionality tests
x_axis = array([1, 2, 3, 4, 5])

y_axis = array([2, 4, 1, 5, 3])

plt.plot(x_axis, y_axis)
plt.title('Application Conversion Test Plot')
plt.xlabel('X Coordinates')
plt.ylabel('Y Coordinates')
plt.grid(True)

plt.show()