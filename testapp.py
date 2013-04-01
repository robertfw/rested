import logging

import motor
import rested
import datetime
import bson


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


class MongoResourceEncoder(rested.ResourceEncoder):
    def default(self, obj):
        if isinstance(obj, bson.objectid.ObjectId):
            return str(obj)
        elif isinstance(obj, datetime.datetime):
            return obj.isoformat()
        else:
            return super(MongoResourceEncoder, self).default(obj)


if __name__ == '__main__':
    rested.run_server(
        root=Root(),
        prefix='api',
        debug=True,
        gzip=True,
        encoder=MongoResourceEncoder,
        resource_kwargs={
            'db': lambda: motor.MotorClient().open_sync()['test']
        })
