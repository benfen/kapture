from kubernetes import client


def get_name(spec):
    """Retrieves the name from the provided Kubernetes object

    Args:
        spec - Spec for a properly constructed kubernetes object

    Returns:
        The name of the Kubernetes object as a string
    """
    return spec["metadata"]["name"]


def evaluate_request(req, allowed_statuses=[404]):
    """Evaluates a request

    This takes a future representing a request to the Kubernetes API and resolves it.  If the request
    succeeds or fails with one of the provided statuses, this method will complete without raising
    an exception

    Args:
        req - Future representing a request to the Kubernetes API
        allowed_statuses - List of numerical HTTP statuses that are to be considered allowed failures.
            This default to [404], which swallows errors if the resource cannot be found

    Raises:
        ApiExcpetion - Raised when the future returns a status not within the list of allowed statuses
    """
    try:
        req.get()
    except client.rest.ApiException as e:
        if e.status not in allowed_statuses:
            raise e
