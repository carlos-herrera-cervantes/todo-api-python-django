from rest_framework import status
from bson.json_util import dumps, loads
from bson.objectid import ObjectId
from django.utils.decorators import classonlymethod
from django.views.generic import View
from django.http.response import HttpResponse

from ..repositories.user_repository import UserRepository
from ..managers.user_manager import UserManager
from ..managers.todo_manager import TodoManager
from ..decorators.user_decorator import exists_user, validate_user
from ..decorators.common_decorator import authorize_request, validate_pagination, validate_role
from ..models.roles import Role
from ..modules.common_module import get_paginate_object

import json
import asyncio

class UserList(View):

    def __init__(self, user_repository=UserRepository(), user_manager=UserManager()):
        self.user_repository = user_repository
        self.user_manager = user_manager

    @classonlymethod
    def as_view(cls, **initkwargs):
        view = super().as_view(**initkwargs)
        view._is_coroutine = asyncio.coroutines._is_coroutine
        return view

    @authorize_request
    @validate_role([Role.ADMIN.value, Role.CLIENT.value])
    @validate_pagination
    async def get(self, request, format=None):
        users = await self.user_repository.get_all(request.GET)
        total_docs = await self.user_repository.count()
        response = { 'status': True, 'data': users }

        if not request.GET.get('paginate'):
            return HttpResponse(dumps(response))
        
        paginate_object = get_paginate_object(request.GET, total_docs)
        response['paginate'] = paginate_object
        return HttpResponse(dumps(response))

    @validate_user
    async def post(self, request, format=None):
        data = loads(request.body)
        user = await self.user_manager.create(data)
        response = {'status': True, 'data': user }
        return HttpResponse(dumps(response), status=status.HTTP_201_CREATED)


class UserDetail(View):

    def __init__(self, user_repository=UserRepository(), user_manager=UserManager(), todo_manager=TodoManager()):
        self.user_repository = user_repository
        self.user_manager = user_manager
        self.todo_manager = todo_manager

    @classonlymethod
    def as_view(cls, **initkwargs):
        view = super().as_view(**initkwargs)
        view._is_coroutine = asyncio.coroutines._is_coroutine
        return view

    @authorize_request
    @validate_role([Role.ADMIN.value, Role.CLIENT.value])
    @exists_user
    async def get(self, request, user_id, format=None):
        user_retrieved = await self.user_repository.get_by_id(user_id, request.GET)
        response = {'status': True, 'data': user_retrieved }
        return HttpResponse(dumps(response))

    @authorize_request
    @validate_role([Role.ADMIN.value, Role.CLIENT.value])
    @exists_user
    async def patch(self, request, user_id, format=None):
        data = loads(request.body)
        user = await self.user_manager.update(user_id, data)
        response = { 'status': True, 'data': user }
        return HttpResponse(dumps(response))

    @authorize_request
    @validate_role([Role.ADMIN.value, Role.CLIENT.value])
    @exists_user
    async def delete(self, request, user_id, format=None):
        await self.user_manager.delete(user_id)
        await self.todo_manager.delete_many({ 'user_id': ObjectId(user_id) })
        return HttpResponse(status=status.HTTP_204_NO_CONTENT)