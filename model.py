import numpy as np

# Training data
X = np.array([[0], [1], [2], [3]], dtype=float)
Y = np.array([[0], [1], [4], [9]], dtype=float)

# Start with a random weight
weight = np.random.randn(1)

learning_rate = 0.01

# Train
for epoch in range(5000):

    # Prediction
    prediction = X * weight

    # Error
    error = prediction - Y

    # How much to change the weight
    gradient = np.mean(2 * X * error)

    # Update the weight
    weight -= learning_rate * gradient

print("Training finished!")
print("Learned weight:", weight)

# Test
test = np.array([[4]], dtype=float)
result = test * weight

print("Prediction for 4:", result)