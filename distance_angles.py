import math

# Calculate the magnitude (length) of a 2D vector
def magnitude_2d(vec):
    x, y = vec
    return math.sqrt(x**2 + y**2)

# Compute the dot product of two 2D vectors
def dot_product_2d(vec1, vec2):
    x1, y1 = vec1
    x2, y2 = vec2
    return x1 * x2 + y1 * y2

# Calculate the angle (in degrees) between two 2D vectors
def angle_between_2d(vec1, vec2):
    dot = dot_product_2d(vec1, vec2)
    mag1 = magnitude_2d(vec1)
    mag2 = magnitude_2d(vec2)
    
    # Prevent division by zero
    if mag1 == 0 or mag2 == 0:
        return 0.0
    
    # Calculate cosine of the angle and clamp to avoid floating-point issues
    cos_theta = dot / (mag1 * mag2)
    cos_theta = max(min(cos_theta, 1), -1)
    
    # Convert the angle from radians to degrees
    theta_radians = math.acos(cos_theta)
    theta_degrees = math.degrees(theta_radians)
    return theta_degrees

# Calculate the Euclidean distance between two 2D points
def distance_2d(p1, p2):
    x1, y1 = p1
    x2, y2 = p2
    return math.sqrt((x2 - x1)**2 + (y2 - y1)**2)

# Main section to test our functions
if __name__ == "__main__":
    # Define two points (or vectors) in 2D space
    pointA = (3, 4)
    pointB = (1, 2)
    
    # Calculate magnitudes for each vector (from origin to the point)
    magA = magnitude_2d(pointA)
    magB = magnitude_2d(pointB)
    
    # Calculate the angle between the two vectors
    angleAB = angle_between_2d(pointA, pointB)
    
    # Calculate the distance between the two points
    dist = distance_2d(pointA, pointB)
    
    # Output the results
    print("Point A:", pointA, "Magnitude:", magA)
    print("Point B:", pointB, "Magnitude:", magB)
    print("Angle between A and B (degrees):", angleAB)
    print("Distance between A and B:", dist)
