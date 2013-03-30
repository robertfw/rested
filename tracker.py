import logging
import rested

logging.basicConfig(level=logging.DEBUG)


class Users(rested.Resource):
    obj = {
        1: rested.Resource({
            'name': 'User 1',
            'email': 'example@example.com'
        }),
        2: rested.Resource({
            'name': 'User 2',
            'email': 'example@example.com'
        })
    }


class Root(rested.Resource):
    obj = {
        'users': Users()
    }

if __name__ == '__main__':
    rested.run_server(Root(), prefix='api', debug=True, gzip=True)
