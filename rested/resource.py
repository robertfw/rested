import json


class RestedException(Exception):
    pass


class NotAuthorizedForResource(RestedException):
    code = 403


class NotFound(RestedException):
    code = 404


class Error(RestedException):
    code = 500


def traverse_resource_tree(root, path):
    '''Given a root object (anything subscriptable will do) and a path,
       will recursively dig into the object tree until it finds the requested
       resource.

       JSON array indexes are always strings, whereas quite often we want to
       use an integer. If a given key is all digits, it will be cast to int

       Will return the object it found, or raise a tornado.web.HTTPError
    '''
    # break the path into two parts
    bits = path.split('/', 1)
    try:
        key = bits[0]

        if key.isdigit():
            key = int(key)

        remaining_path = bits[1] if len(bits) > 1 else None

        # check the root object at the requested index
        node = root[key]

        # if we have path remaining, recurse using the node we just
        # found as the new root, using whatever is left of the path
        if remaining_path:
            return traverse_resource_tree(node, remaining_path)
        else:
            # otherwise, return the node we found
            return node
    except (TypeError, KeyError):
        # TypeError is thrown on non-subscriptable nodes,
        # KeyError for subscriptable nodes that are missing the key
        raise NotFound()


class Resource(object):
    '''Base implementation of a resource
       Defines basic handlers for working with self.obj, and provides
       subscriptable behaviour in __getitem__
    '''
    def __init__(self, obj=None):
        if obj:
            self.obj = obj

    def get(self, handler=None, *args, **kwargs):
        return handler.finish(code=200, content=self.obj)

    def post(self, *args, **kwargs):
        raise NotImplemented()

    def put(self, *args, **kwargs):
        raise NotImplemented()

    def delete(self, *args, **kwargs):
        raise NotImplemented()

    def patch(self, *args, **kwargs):
        raise NotImplemented()

    def options(self, *args, **kwargs):
        raise NotImplemented()

    def head(self, *args, **kwargs):
        raise NotImplemented()

    def __getitem__(self, key):
        '''Check our obj for key, and if it is a Resource, return it
           Otherwise, raise a 404
        '''
        try:
            if isinstance(self.obj[key], Resource):
                return self.obj[key]
        except KeyError:
            pass

        raise NotFound()


class ResourceEncoder(json.JSONEncoder):
    '''Used to convert Resource objects into json
       When encoding a Resource object, it will encode resource.obj
       Otherwise, just use normal behaviour
    '''
    def default(self, obj):
        if isinstance(obj, Resource):
            return obj.obj  # that's an unfortunate coincidence of naming
        else:
            return super(ResourceEncoder, self).default(obj)
