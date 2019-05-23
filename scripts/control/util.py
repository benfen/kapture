from kubernetes import client


def get_name(spec):
    return spec["metadata"]["name"]


def evaluate_request(req, allowed_statuses=[404]):
    try:
        req.get()
    except client.rest.ApiException as e:
        if e.status not in allowed_statuses:
            raise e
