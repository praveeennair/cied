from rest_framework.response import Response
from rest_framework import status


def response_template(
        data=None, status=status.HTTP_200_OK,
        success=True, message=[]):
    response_dict = {
        'success': success,
        'data': data,
        'errors': message
    }
    return Response(status=status, data=response_dict)


def success_response(data=None):
    return response_template(data)


def general_error_response(message, data=None):
    return response_template(
        data, status.HTTP_400_BAD_REQUEST, False, [message])


def unauthorized_error_response(message, data=None):
    return response_template(
        data, status.HTTP_401_UNAUTHORIZED, False, [message])


def not_found_response(message, data=None):
    return response_template(
        data, status.HTTP_404_NOT_FOUND, False, [message])
