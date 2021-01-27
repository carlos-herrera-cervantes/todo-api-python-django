from bson.objectid import ObjectId
from bson.json_util import dumps, loads
from asgiref.sync import sync_to_async

from ..modules.mongodb_module import build_lookup_filter, build_paginate_filter, build_sort_filter
from ..models.config import Config
from ..models.user import User
from ..modules.common_module import parse_pages, get_type_ordering_object
from ..serializers.common_serializer import default

import json

Config.connect()

class UserRepository:

    @sync_to_async
    def get_all(self, query_params):
        """
        Return all users
        Parameters
        ----------
        query_params: dict
            Dictionary with query params of request
        """
        exists_page = query_params.get('page')
        exists_with = query_params.get('with')
        exists_sort = query_params.get('sort') if query_params.get('sort') else 'first_name'

        if not exists_with and not exists_page:
            users = User.objects().order_by(exists_sort).to_json()
            return json.loads(users, object_hook=default)

        if exists_with and not exists_page:
            pipeline = build_lookup_filter(exists_with, 'user')
            users = User.objects().aggregate(*pipeline)
            return json.loads(dumps(users), object_hook=default)

        pages = parse_pages(query_params)
        page = pages['page']
        page_size = pages['page_size']

        if exists_page and exists_with:
            partial_pipeline = build_lookup_filter(exists_with, 'user')
            partial_pipeline = build_sort_filter(get_type_ordering_object(exists_sort), partial_pipeline)
            users = User.objects().aggregate(*build_paginate_filter(page, page_size, partial_pipeline))
            return json.loads(dumps(users), object_hook=default)

        return json.loads(User.objects().order_by(exists_sort).skip(page).limit(page_size).to_json(), object_hook=default)

    @sync_to_async
    def get_by_id(self, id, query_params):
        """
        Return a specific user
        Parameters
        ----------
        id: string
            The specific user ID to retrieve
        query_params: dict
            Dictionary with query params of request
        """
        exists_with = query_params.get('with')

        if exists_with and not exists_with == 'user':
            pipeline = build_lookup_filter(exists_with, 'user')
            pipeline.append({ '$match': { '_id': ObjectId(id) } })
            return json.loads(dumps(User.objects().aggregate(*pipeline)), object_hook=default)

        user = User.objects.get(id=ObjectId(id))
        return json.loads(user.to_json(), object_hook=default)

    @sync_to_async
    def get_one(self, filter):
        """
        Return a specific user by criteria
        Parameters
        ----------
        filter: dict
            The specific user criteria to retrieve
        """
        user = User.objects(__raw__=filter)
        return user

    @sync_to_async
    def count(self, filter={}):
        """
        Return total of documents
        Parameters
        ----------
        filter: dict
            The specific user criteria to count
        """
        return User.objects(__raw__=filter).count()