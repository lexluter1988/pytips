from flask_restful import Resource, Api

api = Api(prefix="/api/v1")


@api.resource('/greetings')
class Greet(Resource):
    def get(self):
        return 'Greetings from api!'
