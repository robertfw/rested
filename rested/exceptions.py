class RestedException(Exception):
    pass


class ResourceNotFound(RestedException):
    pass


class ServerError(RestedException):
    pass
