import logging
import json

import tornado.autoreload
import tornado.httpserver
import tornado.ioloop
import tornado.web


logger = logging.getLogger(__name__)


class ResourceNotFound(Exception):
    pass

class ServerError(Exception):
    pass


class Resource(object):
    '''Base implementation of a resource
       Defines basic handlers for working with self.obj, and provides
       subscriptable behaviour in __getitem__
    '''
    def __init__(self, obj=None):
        if obj:
            self.obj = obj

    def get(self, handler=None, *args, **kwargs):
        return handler.write_response(200, self.obj)

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
            return super(ResourceEncoder, self).default(obj)


class RootHandler(tornado.web.RequestHandler):
    '''The entry point for our api

       When initializing, you must provide the root object
       You may optionally pass an encoder that will be passed
       to json.dumps.
    '''
    def initialize(self, root, encoder=None):
        self.root = root
        self.encoder = encoder

    def write_content(self, content):
        logger.debug('writing content...')
        self.write(json.dumps(content, cls=self.encoder, indent=4))

    def finish(self, code=None, content=None):
        if content is not None:
            self.write_content(content)

        if code is not None:
            self.set_status(code)

        super(RootHandler, self).finish()

    @tornado.web.asynchronous
    def handle(self, path):
        self.set_header('Content-Type', 'application/json')
        try:
            # Find the requested resource, and call the requested method
            # The resource should return an HTTP code and some content
            # If we get a ResourceNotFound, raise a 404 error
            try:
                resource_kwargs = self.settings.get('resource_kwargs', {})
                getattr(
                    traverse_resource_tree(self.root, path),
                    self.request.method.lower()
                )(handler=self, **resource_kwargs)
            except ServerError:
                raise tornado.web.HTTPError(500)
            except ResourceNotFound:
                raise tornado.web.HTTPError(404)

        except tornado.web.HTTPError as exc:
            self.send_error(status_code=exc.status_code)

    # Tie all of our methods into the handle method
    get = handle
    post = handle
    put = handle
    delete = handle
    head = handle
    options = handle


def run_server(
    root,
    resource_kwargs=None,
    prefix='',
    port=8000,
    encoder=None,
    debug=False,
    **kwargs
):
    '''Fires up the rested server
       You must pass in a root resource,
       Optionally you may provide:

       port: int, what port to bind to (default 8000)

       prefix: string, url prefix (default '')

       lazy_app_settings: a dictionary of callables, once the server is
       started, they will be run and their return values added to the
       application settings for their respective keys. This is useful
       for anything that needs to be initialized after the server starts,
       like a Motor db

       debug: True / False

       any other keyword arguments will be passed to the tornado application
    '''

    # setup our main application, passing through any kwargs
    app = tornado.web.Application(
        handlers=[(r"/{prefix}/(.*)".format(prefix=prefix), RootHandler, {
            'root': root,
            'encoder': encoder if encoder else ResourceEncoder
        })],
        debug=debug,
        **kwargs
    )

    app.listen(port)

    # setup any kwargs being provided to resources
    app.settings['resource_kwargs'] = {
        key: value() if callable(value) else value
        for key, value in resource_kwargs.items()
    }

    tornado.ioloop.IOLoop.instance().start()
