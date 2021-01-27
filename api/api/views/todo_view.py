from rest_framework import status
from bson.json_util import dumps, loads
from bson.objectid import ObjectId
from django.utils.decorators import classonlymethod
from django.views.generic import View
from django.http.response import HttpResponse

from ..repositories.user_repository import UserRepository
from ..repositories.todo_repository import TodoRepository
from ..managers.todo_manager import TodoManager
from ..managers.user_manager import UserManager
from ..modules.user_module import add_todo_to_user, delete_todo_of_user
from ..decorators.todo_decorator import exists_todo, validate_todo
from ..decorators.user_decorator import exists_user
from ..decorators.common_decorator import authorize_request, validate_pagination, validate_role
from ..models.roles import Role
from ..modules.common_module import get_paginate_object

import json
import asyncio

class TodoList(View):

    def __init__(
        self, 
        todo_repository=TodoRepository(), 
        todo_manager=TodoManager(), 
        user_repository=UserRepository(),
        user_manager=UserManager()):
        self.todo_repository = todo_repository
        self.todo_manager = todo_manager
        self.user_repository = user_repository
        self.user_manager = user_manager

    @classonlymethod
    def as_view(cls, **initkwargs):
        view = super().as_view(**initkwargs)
        view._is_coroutine = asyncio.coroutines._is_coroutine
        return view

    @authorize_request
    @validate_role([Role.ADMIN.value, Role.CLIENT.value])
    @exists_user
    @validate_pagination
    async def get(self, request, user_id, format=None):
        todos = await self.todo_repository.get_all(request.GET, { 'user_id': ObjectId(user_id) })
        total_docs = await self.todo_repository.count()
        response = { 'status': True, 'data': todos }

        if not request.GET.get('paginate'):
            return HttpResponse(dumps(response))

        paginate_object = get_paginate_object(request.GET, total_docs)
        response['paginate'] = paginate_object
        return HttpResponse(dumps(response))

    @authorize_request
    @validate_role([Role.ADMIN.value, Role.CLIENT.value])
    @exists_user
    @validate_todo
    async def post(self, request, user_id, format=None):
        todo = loads(request.body)
        todo['user_id'] = user_id
        result = await self.todo_manager.create(todo)
        response = {'status': True, 'data': result }
        await add_todo_to_user(self, user_id, result['id'], request)
        return HttpResponse(dumps(response), status=status.HTTP_201_CREATED)

class TodoDetail(View):

    def __init__(
        self, 
        todo_repository=TodoRepository(), 
        todo_manager=TodoManager(), 
        user_repository=UserRepository(),
        user_manager=UserManager()):
        self.todo_repository = todo_repository
        self.todo_manager = todo_manager
        self.user_repository = user_repository
        self.user_manager = user_manager

    @classonlymethod
    def as_view(cls, **initkwargs):
        view = super().as_view(**initkwargs)
        view._is_coroutine = asyncio.coroutines._is_coroutine
        return view

    @authorize_request
    @validate_role([Role.ADMIN.value, Role.CLIENT.value])
    @exists_user
    @exists_todo
    async def get(self, request, user_id, todo_id, format=None):
        todo = await self.todo_repository.get_by_id(todo_id, request.GET)
        response = {'status': True, 'data': todo }
        return HttpResponse(dumps(response))

    @authorize_request
    @validate_role([Role.ADMIN.value, Role.CLIENT.value])
    @exists_user
    @exists_todo
    async def patch(self, request, user_id, todo_id, format=None):
        data = loads(request.body)
        todo = await self.todo_manager.update(todo_id, data)
        response = { 'status': True, 'data': todo }
        return HttpResponse(dumps(response))

    @authorize_request
    @validate_role([Role.ADMIN.value, Role.CLIENT.value])
    @exists_user
    @exists_todo
    async def delete(self, request, user_id, todo_id, format=None):
        await self.todo_manager.delete(todo_id)
        await delete_todo_of_user(self, user_id, todo_id, request)
        return HttpResponse(status=status.HTTP_204_NO_CONTENT)