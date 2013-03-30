from resource import Resource


class Users(Resource):
    obj = {
        1: Resource({
            'name': 'User 1',
            'email': 'example@example.com'
        }),
        2: Resource({
            'name': 'User 2',
            'email': 'example@example.com'
        })
    }


root = {
    'users': Users()
}
