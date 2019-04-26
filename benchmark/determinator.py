from math import sqrt

def distance_to_line(point, line):
    """Calculates the shortest distance from the given point to the line.

    Args:
        point: A tuple containing the (x, y) coordinates of the point
        line: A tuple (a, b) defining a linear line y = a + bx

    Returns:
        The distance between the point and the line represented as a float point
    """
    x, y = point

    a = line[1] * -1
    b = 1
    c = line[0] * -1

    return abs(a * x + b * y + c) / sqrt(a ** 2 + b ** 2)

def simple_linear_regression(x_arr, y_arr):
    """Performs a simple linear regression

    Args:
        x_arr: An array containing all of the x values of the points
        y_arr: An array containing all of the y values of the points.  This should be the same length as the x_arr.

    Returns:
        A tuple (a, b) defining a linear line y = a + bx
    """

    points = len(x_arr)

    sum_x = sum(x_arr)
    sum_y = sum(y_arr)
    sum_x_squared = sum( [ x_arr[i] ** 2 for i in range(points) ] )
    dot_product = sum( [ x_arr[i] * y_arr[i] for i in range(points) ] )

    denominator = (points * sum_x_squared - sum_x ** 2)
    a = (sum_y * sum_x_squared - sum_x * dot_product) / denominator
    b = (points * dot_product - sum_x * sum_y) / denominator

    return (a, b)
