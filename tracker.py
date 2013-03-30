import logging

import tornado.ioloop
import tornado.gen

import motor
import rested

# just log to the console for now
logging.basicConfig(level=logging.DEBUG)


# The users of our application
class Users(rested.Resource):
    obj = {
        1: rested.Resource({
            'name': 'User 1',
            'email': 'example@example.com',
            'password': 'test'
        }),
        2: rested.Resource({
            'name': 'User 2',
            'email': 'example@example.com',
            'password': 'test'
        })
    }


class Root(rested.Resource):
    obj = {
        'users': Users()
    }

if __name__ == '__main__':
    rested.run_server(
        root=Root(),
        prefix='api',
        debug=True,
        gzip=True,
        resource_kwargs={
            'db': lambda: motor.MotorClient().open_sync()['test']
        })
