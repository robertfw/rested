import json
import logging

logger = logging.getLogger(__name__)


class ResourceNotFound(Exception):
    pass


class Resource(object):
    '''Base implementation of a resource
       Defines basic handlers for working with self.obj, and provides
       subscriptable behaviour in __getitem__
    '''
    def __init__(self, obj=None):
        if obj:
            self.obj = obj

    def get(self):
        return 200, self.obj

    def post(self):
        pass

    def put(self):
        pass

    def delete(self):
        pass

    def patch(self):
        pass

    def options(self):
        pass

    def head(self):
        pass

    def __getitem__(self, key):
        '''Check our obj for key, and if it is a Resource, return it
           Otherwise, raise a 404
        '''
        try:
            if isinstance(self.obj[key], Resource):
                return self.obj[key]
        except KeyError:
            pass

        raise ResourceNotFound()


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
        logging.debug('Checking key "{key} [{type}]"'.format(
            key=bits[0],
            type=type(key)))

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
        raise ResourceNotFound


class ResourceEncoder(json.JSONEncoder):
    '''Used to convert Resource objects into json
       When encoding a Resource object, it will encode resource.obj
       Otherwise, just use normal behaviour
    '''
    def default(self, obj):
        if isinstance(obj, Resource):
            return obj.obj  # that's an unfortunate coincidence of naming
        else:
            return super().default(self, obj)
