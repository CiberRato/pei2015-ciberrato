from rest_framework.exceptions import APIException


class NotFound(APIException):
    status_code = 404

    def __init__(self, message):
        super(NotFound, self).__init__(detail=message)


class Forbidden(APIException):
    status_code = 403

    def __init__(self, message):
        super(Forbidden, self).__init__(detail=message)


class BadRequest(APIException):
    status_code = 400

    def __init__(self, message):
        super(BadRequest, self).__init__(detail=message)