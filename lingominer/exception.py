
class LingominerException(Exception):
    pass


class ResourceException(LingominerException):
    pass


class ResourceNotFound(ResourceException):
    pass


class ResourceConflict(ResourceException):
    pass
