# -*- coding: utf-8 -*-
"""
Created on Mon May 12 14:56:05 2025

@author: Eian
"""
import numpy as np

# Desired size of each subset (row)
subset_size = 4



binary_string = '11100001010110101110100010010011'
binary_array = np.frombuffer(binary_string.encode('ascii'), dtype='u1') - ord('0') # or dtype=int8, int
print(binary_array)  # Output: [0 1 0 1 1 0 0 1]

# Calculate the number of subsets (rows)
num_subsets = len(binary_array) // subset_size
binary_array_2d = binary_array.reshape(num_subsets, subset_size)

powers_of_2 = 2 ** np.arange(binary_array_2d.shape[1] - 1, -1, -1)
print("Powers of 2 for each bit position:", powers_of_2)

# Multiply each bit by its corresponding power of 2 and sum along each row
int_vector_1d = np.sum(binary_array_2d * powers_of_2, axis=1)

print("Resulting 1D vector of integers:", int_vector_1d)

points = np.array([-0.75+0.75j,-0.25-0.75j,0.75-0.75j, 0.25-0.75j,0.75-0.25j, 0.25-0.25j, -0.75-0.25j, -0.25-0.25j, 0.75+0.75j, 0.25+0.75j, -0.75-0.75j, -0.25+0.75j, -0.75+0.25j,-0.25+0.25j, 0.75+0.25j, 0.25+0.25j])
cplx_msg = points[int_vector_1d]
print("Resulting Complex Message:", cplx_msg)