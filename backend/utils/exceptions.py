from rest_framework import status
from rest_framework.exceptions import APIException

class NotValid(APIException):
    status_code = status.HTTP_402_PAYMENT_REQUIRED
    default_detail = 'commited sql were not valid.'
    default_code = 'invalid'
