import logging
import json

import tornado.httpserver
import tornado.ioloop
import tornado.web

import resource

import tracker

logging.basicConfig(level=logging.DEBUG)
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

    def handle(self, path):
        try:
            # Find the requested resource, and call the requested method
            # The resource should return an HTTP code and some content
            # If we get a ResourceNotFound, raise a 404 error
            try:
                code, content = getattr(
                    resource.traverse_resource_tree(self.root, path),
                    self.request.method.lower()
                )()
            except resource.ResourceNotFound:
                raise tornado.web.HTTPError(404)

            self.set_header('Content-Type', 'application/json')
            self.write(json.dumps(content, cls=self.encoder, indent=4))
            self.set_status(code)
        except tornado.web.HTTPError as exc:
            self.send_error(status_code=exc.status_code)

    # Tie all of our methods into the handle method
    get = handle
    post = handle
    put = handle
    delete = handle
    head = handle
    options = handle

if __name__ == '__main__':
    app = tornado.web.Application(
        debug=True,
        gzip=True,
        handlers=[(r"/api/(.*)", RootHandler, {
            'root': tracker.root,
            'encoder': resource.ResourceEncoder
        })]
    )

    http_server = tornado.httpserver.HTTPServer(app)
    http_server.listen(8000)
    tornado.ioloop.IOLoop.instance().start()
