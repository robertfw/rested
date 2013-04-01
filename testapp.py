import logging

import motor
import rested


# just log to the console for now
logging.basicConfig(level=logging.DEBUG)

logger = logging.getLogger(__name__)


# The users of our application
class Users(rested.Resource):
    def get(self, db=None, handler=None):
        def got_users(users, error):
            if error:
                #TODO: implement error handling here
                pass

            handler.finish(code=200, content=users)

        db.users.find().to_list(callback=got_users)


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
