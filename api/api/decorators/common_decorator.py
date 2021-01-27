from functools import wraps
from rest_framework import status
from bson.json_util import dumps, loads
from django.http.response import HttpResponse
from django.utils.translation import gettext as _
from django.conf import settings

import jwt
import datetime

def authorize_request(fn):
    """
    Validates token of request
    """
    @wraps(fn)
    async def inner(*args, **kwargs):
        body = { 'status': False, 'message': _('Invalid json web token'), 'code': 'InvalidToken' }
        response = HttpResponse(dumps(body), status=status.HTTP_401_UNAUTHORIZED)

        try:
            headers = args[1].headers
            token = headers.get('authorization')

            if token is None:
                return response

            jwt.decode(token.split(' ').pop(), settings.SECRET_KEY, algorithms=['HS256'])
            return await fn(*args, **kwargs)
        except Exception:
            return response
    return inner

def validate_pagination(fn):
    """
    Validates pagination params
    """
    @wraps(fn)
    async def inner(*args, **kwargs):
        paginate = args[1].GET.get('paginate')
        page = args[1].GET.get('page')
        page_size = args[1].GET.get('page_size')

        if not paginate:
            return await fn(*args, **kwargs)

        response_missing_params = { 
            'status': False, 
            'message': _('page or page_size parameter is missing.'), 
            'code': 'MissingPaginateParams' 
        }

        if paginate and (not page or not page_size):
            return HttpResponse(dumps(response_missing_params), status=status.HTTP_400_BAD_REQUEST)

        response_invalid_params = { 
            'status': False, 
            'message': _('The value of page must be greater than 0 / Tha value of page_size must be greater than 0 and less than 100.'), 
            'code': 'InvalidPagination' 
        }

        if int(page) < 1 or int(page_size) < 1 or int(page_size) > 100:
            return HttpResponse(dumps(response_invalid_params), status=status.HTTP_400_BAD_REQUEST)

        return await fn(*args, **kwargs)
    return inner

def validate_role(roles):
    """
    Validates role of user
    Parameters
    ----------
    roles: array
        Roles which this operation admits
    """
    def wrap(fn):
        async def inner(*args, **kwargs):
            headers = args[1].headers
            token = headers.get('authorization')
            payload = jwt.decode(token.split(' ').pop(), settings.SECRET_KEY, algorithms=['HS256'])
            role = payload['role']
            response = { 
                'status': False, 
                'message': _('You do not have sufficient permissions to do this operation.'), 
                'code': 'InvalidPermissions' 
            }

            if role not in roles:
                return HttpResponse(dumps(response), status=status.HTTP_403_FORBIDDEN)

            result = await fn(*args, **kwargs)
            return result
        return inner
    return wrap