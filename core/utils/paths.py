import numpy as np

STRAIGHT_PATH_THRESHOLD = 1e-9
OUT = np.array([0.0, 0.0, 1.0])


def straight_path(start_points, end_points, alpha):
    """Linearly interpolate between start and end points."""
    return (1.0 - alpha) * start_points + alpha * end_points


def normalize(vector, fall_back=None):
    """Normalize a vector, returning fall_back if vector has zero length."""
    norm = np.linalg.norm(vector)
    if norm < 1e-12:
        if fall_back is None:
            return np.zeros_like(vector)
        return fall_back
    return vector / norm


def rotation_matrix(angle, axis):
    """Create a rotation matrix for a given angle around an axis.

    Uses Rodrigues' rotation formula.
    """
    axis = normalize(axis, fall_back=OUT)
    cos_a = np.cos(angle)
    sin_a = np.sin(angle)
    # Rodrigues' rotation formula: R = I + sin(a)*K + (1-cos(a))*K^2
    # where K is the cross-product matrix of axis
    K = np.array([
        [0.0, -axis[2], axis[1]],
        [axis[2], 0.0, -axis[0]],
        [-axis[1], axis[0], 0.0],
    ])
    return np.eye(3) + sin_a * K + (1.0 - cos_a) * np.dot(K, K)


def path_along_arc(arc_angle, axis=OUT):
    """Returns a path function that moves points along a circular arc.

    The arc traverses from start_points to end_points with the given
    arc_angle (in radians). The axis determines the plane of rotation.
    """
    if abs(arc_angle) < STRAIGHT_PATH_THRESHOLD:
        return straight_path

    unit_axis = normalize(axis, fall_back=OUT)

    def path(start_points, end_points, alpha):
        vects = end_points - start_points
        centers = start_points + 0.5 * vects
        if arc_angle != np.pi:
            centers += np.cross(unit_axis, vects / 2.0) / np.tan(arc_angle / 2.0)
        rot_matrix = rotation_matrix(alpha * arc_angle, unit_axis)
        return centers + np.dot(start_points - centers, rot_matrix.T)

    return path
