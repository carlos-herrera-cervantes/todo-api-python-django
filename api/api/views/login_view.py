from django.utils.decorators import classonlymethod
from rest_framework import status
from bson.json_util import dumps, loads
from django.views.generic import View
from django.http.response import HttpResponse
from django.conf import settings

from ..repositories.user_repository import UserRepository
from ..decorators.user_decorator import validate_credentials

import jwt
import json
import asyncio

class Login(View):

    def __init__(self, user_repository=UserRepository()):
        self.user_repository = user_repository

    @classonlymethod
    def as_view(cls, **initkwargs):
        view = super().as_view(**initkwargs)
        view._is_coroutine = asyncio.coroutines._is_coroutine
        return view

    @validate_credentials
    async def post(self, request, format=None):
        data = loads(request.body)
        email = data['email']
        user = await self.user_repository.get_one({ 'email': email })
        token = jwt.encode({ 'email': user.first()['email'], 'role': user.first()['role'] }, settings.SECRET_KEY, algorithm='HS256')
        response = { 'status': True, 'data': token.decode('ascii') }
        return HttpResponse(dumps(response))