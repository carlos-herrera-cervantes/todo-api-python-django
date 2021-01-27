from bson.objectid import ObjectId
from bson.json_util import dumps, loads
from asgiref.sync import sync_to_async

from ..models.config import Config
from ..models.todo import Todo
from ..serializers.common_serializer import default

import json

Config.connect()

class TodoManager:

    @sync_to_async
    def create(self, todo):
        """
        Create new todo
        Parameters
        ----------
        todo: dict
            Todo object to create
        """
        todo = Todo(**todo)
        result = todo.save()
        return json.loads(result.to_json(), object_hook=default)

    @sync_to_async
    def update(self, todo_id, todo):
        """
        Update a specific todo
        Parameters
        ----------
        todo_id: string
            The todo ID to update
        todo: dict
            Todo object to update
        """
        Todo.objects(id=ObjectId(todo_id)).update_one(**todo)
        updated_todo = Todo.objects.get(id=ObjectId(todo_id))
        updated_todo.save()
        return json.loads(updated_todo.to_json(), object_hook=default)

    @sync_to_async
    def delete(self, todo_id):
        """
        Delete a specific todo
        Parameters
        ----------
        todo_id: string
            The todo ID to delete
        """
        Todo.objects(id=ObjectId(todo_id)).delete()
        return True

    @sync_to_async
    def delete_many(self, filter):
        """
        Delete todos by specific filter
        Parameters
        ----------
        filter: dict
            Properties specifying the filter to apply
        """
        Todo.objects(__raw__=filter).delete()
        return True