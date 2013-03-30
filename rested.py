import logging
import json

import tornado.httpserver
import tornado.ioloop
import tornado.web


logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger(__name__)


class RootHandler(tornado.web.RequestHandler):
    def handle(self, path):
        root = {
            'omg': {
                'wtf': {
                    'bbq': BBQ()
                }
            }
        }

        try:
            resource = get_resource(root, path)
            code, content = getattr(resource, self.request.method.lower())()
            self.set_header('Content-Type', 'application/json')
            self.write(json.dumps(content, cls=ResourceEncoder))
            self.set_status(code)
        except tornado.web.HTTPError as exc:
            self.send_error(status_code=exc.status_code)

    get = handle
    post = handle
    put = handle
    delete = handle
    head = handle
    options = handle


class ResourceEncoder(json.JSONEncoder):
    def default(self, obj):
        if isinstance(obj, Resource):
            return obj.obj  # that's an unfortunate coincidence of naming
        else:
            return super().default(self, obj)


class Resource(object):
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
        try:
            if isinstance(self.obj[key], Resource):
                return self.obj[key]
        except KeyError:
            pass

        raise tornado.web.HTTPError(404)


class Awd(Resource):
    obj = {
        'foo': 'bar'
    }


class BBQ(Resource):
    obj = {
        'whammo': 'blammo',
        'awd': Awd()
    }


def get_resource(root_resource, path):
    bits = path.split('/', 1)
    try:
        resource = root_resource[bits[0]]

        if len(bits) > 1:
            resource = get_resource(resource, bits[1])
    except (TypeError, KeyError):
        raise tornado.web.HTTPError(404)

    return resource

if __name__ == '__main__':
    app = tornado.web.Application(
        debug=True,
        gzip=True,
        handlers=[(r"/api/(.*)", RootHandler)]
    )
    http_server = tornado.httpserver.HTTPServer(app)
    http_server.listen(8000)
    tornado.ioloop.IOLoop.instance().start()
