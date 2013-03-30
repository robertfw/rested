from resource import Resource


class Users(Resource):
    obj = {
        1: Resource({
            'name': 'Robert',
            'email': 'radicalphoenix@gmail.com'
        }),
        2: Resource({
            'name': 'Helene',
            'email': 'helenesofiewarner@gmail.com'
        })
    }


root = {
    'users': Users()
}
