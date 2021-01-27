from functools import wraps
from rest_framework import status
from bson.json_util import dumps, loads
from django.http.response import HttpResponse
from django.utils.translation import gettext as _
from mongoengine.errors import DoesNotExist, ValidationError

from ..models.user import User

import bcrypt

def exists_user(fn):
    """
    Validates if user exists in the collection
    """
    @wraps(fn)
    async def inner(*args, **kwargs):
        try:
            await args[0].user_repository.get_by_id(kwargs['user_id'], args[1].GET)
            return await fn(*args, **kwargs)
        except DoesNotExist:
            response = { 'status': False, 'message': _('User not found'), 'code': 'UserNotFound' }
            return HttpResponse(dumps(response), status=status.HTTP_404_NOT_FOUND)
    return inner

def validate_user(fn):
    """
    Validates fields of user
    """
    @wraps(fn)
    async def inner(*args, **kwargs):
        try:
            data = loads(args[1].body)
            user = User(**data)
            user.validate()
            return await fn(*args, **kwargs)
        except ValidationError as ex:
            dict = ex.__dict__
            errors = ''

            for key, value in dict['errors'].items():
                errors += f'\n {key} {value} \n'

            response = { 'status': False, 'message': _('User not valid') + ' ' + errors, 'code': 'UserNotValid' }
            return HttpResponse(dumps(response), status=status.HTTP_422_UNPROCESSABLE_ENTITY)
    return inner

def validate_credentials(fn):
    """
    Validates credentials of user
    """
    @wraps(fn)
    async def inner(*args, **kwargs):
        response_not_found_user = { 'status': False, 'message': _('User not found'), 'code': 'UserNotFound' }
        response = HttpResponse(dumps(response_not_found_user), status=status.HTTP_404_NOT_FOUND)

        try:
            data = loads(args[1].body)
            email = data['email']
            password_sended = data['password']
            user = await args[0].user_repository.get_one({ 'email': email })
            password_retrieved = user.first()['password']

            if bcrypt.checkpw(password_sended.encode('utf-8'), password_retrieved.encode('utf-8')):
                return await fn(*args, **kwargs)

            response_wrong_credentials = { 'status': False, 'message': _('Wrong credentials'), 'code': 'WrongCredentials' }
            return HttpResponse(dumps(response_wrong_credentials), status=status.HTTP_400_BAD_REQUEST)
        except DoesNotExist:
            return response
        except TypeError:
            return response
    return inner