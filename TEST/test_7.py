import numpy as np

# Define the 2x2 array
arr = np.array([[1, 2,2], [1, 2,2]])

# Calculate the standard deviation of each subarray
stddevs = np.apply_along_axis(np.std, 1, arr)

# Print the results
print(stddevs)
