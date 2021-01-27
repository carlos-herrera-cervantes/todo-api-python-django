from bson.objectid import ObjectId
from bson.json_util import dumps, loads
from asgiref.sync import sync_to_async

from ..modules.mongodb_module import build_lookup_filter, build_paginate_filter, build_sort_filter
from ..models.config import Config
from ..models.todo import Todo
from ..modules.common_module import parse_pages, get_type_ordering_object
from ..serializers.common_serializer import default

import json

Config.connect()

class TodoRepository:

    @sync_to_async
    def get_all(self, query_params, filter={}):
        """
        Return all todos
        Parameters
        ----------
        query_params: dict
            Dictionary with query params of request
        """
        exists_page = query_params.get('page')
        exists_with = query_params.get('with')
        exists_sort = query_params.get('sort') if query_params.get('sort') else 'title'

        if not exists_with and not exists_page:
            todos = Todo.objects(__raw__=filter).order_by(exists_sort).to_json()
            return json.loads(todos, object_hook=default)

        if exists_with and not exists_page:
            pipeline = build_lookup_filter(exists_with, 'todo')
            todos = Todo.objects(__raw__=filter).aggregate(*pipeline)
            return json.loads(dumps(todos), object_hook=default)

        pages = parse_pages(query_params)
        page = pages['page']
        page_size = pages['page_size']

        if exists_page and exists_with:
            partial_pipeline = build_lookup_filter(exists_with, 'todo')
            partial_pipeline = build_sort_filter(get_type_ordering_object(exists_sort), partial_pipeline)
            todos = Todo.objects(__raw__=filter).aggregate(*build_paginate_filter(page, page_size, partial_pipeline))
            return json.loads(dumps(todos), object_hook=default)

        return json.loads(Todo.objects(__raw__=filter).order_by(exists_sort).skip(page).limit(page_size).to_json(), object_hook=default)

    @sync_to_async
    def get_by_id(self, id, query_params):
        """
        Return a specific todo
        Parameters
        ----------
        id: string
            The specific todo ID to retrieve
        query_params: dict
            Dictionary with query params of request
        """
        exists_with = query_params.get('with')

        if not exists_with:
            todo = Todo.objects.get(id=ObjectId(id))
            return json.loads(todo.to_json(), object_hook=default)

        pipeline = build_lookup_filter(exists_with, 'todo')
        pipeline.append({ '$match': { '_id': ObjectId(id) } })
        pipeline.append({ '$unwind': '$user' })
        return json.loads(dumps(Todo.objects().aggregate(*pipeline)), object_hook=default)

    @sync_to_async
    def count(self, filter={}):
        """
        Return total of documents
        Parameters
        ----------
        filter: dict
            The specific user criteria to count
        """
        return Todo.objects().count()