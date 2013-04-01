import json
import logging

import tornado.web

from . import resource

logger = logging.getLogger(__name__)


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
            # It may also throw a derivative of RestedException, which
            # will provide a sensible error code
            try:
                resource_kwargs = self.settings.get('resource_kwargs', {})
                getattr(
                    resource.traverse_resource_tree(self.root, path),
                    self.request.method.lower()
                )(handler=self, **resource_kwargs)
            except resource.RestedException as exc:
                raise tornado.web.HTTPError(exc.code)

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
    prefix='api',
    port=8000,
    gzip=True,
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

    handlers = [
        (r"/{prefix}/(.*)".format(prefix=prefix),
         RootHandler,
         {'root': root,
          'encoder': encoder if encoder else resource.ResourceEncoder}),

        ("/",
         tornado.web.StaticFileHandler,
         {"path": "static"})
    ]

    # setup our main application, passing through any kwargs
    app = tornado.web.Application(
        handlers=handlers,
        debug=debug,
        gzip=gzip,
        **kwargs
    )

    app.listen(port)

    # setup any kwargs being provided to resources
    app.settings['resource_kwargs'] = {
        key: value() if callable(value) else value
        for key, value in resource_kwargs.items()
    }

    tornado.ioloop.IOLoop.instance().start()
