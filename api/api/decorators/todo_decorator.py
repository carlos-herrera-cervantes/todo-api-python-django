from functools import wraps
from rest_framework import status
from bson.json_util import dumps, loads
from django.http.response import HttpResponse
from django.utils.translation import gettext as _
from mongoengine.errors import DoesNotExist, ValidationError

from ..models.todo import Todo

def exists_todo(fn):
    """
    Validates if todo exists in the collection
    """
    @wraps(fn)
    async def inner(*args, **kwargs):
        try:
            await args[0].todo_repository.get_by_id(kwargs['todo_id'], args[1].GET)
            return await fn(*args, **kwargs)
        except DoesNotExist:
            response = { 'status': False, 'message': _('Todo not found'), 'code': 'TodoNotFound' }
            return HttpResponse(dumps(response), status=status.HTTP_404_NOT_FOUND)
    return inner

def validate_todo(fn):
    """
    Validates fields of todo
    """
    @wraps(fn)
    async def inner(*args, **kwargs):
        try:
            data = loads(args[1].body)
            todo = Todo(**data)
            todo.validate()
            return await fn(*args, **kwargs)
        except ValidationError as ex:
            dict = ex.__dict__
            errors = ''

            for key, value in dict['errors'].items():
                errors += f'\n {key} {value} \n'
            response = { 'status': False, 'message': _('Todo not valid') + ' ' + errors, 'code': 'TodoNotValid' }
            return HttpResponse(dumps(response), status=status.HTTP_422_UNPROCESSABLE_ENTITY)
    return inner