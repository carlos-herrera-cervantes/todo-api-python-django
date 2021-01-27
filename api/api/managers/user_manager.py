from bson.objectid import ObjectId
from asgiref.sync import sync_to_async

from ..models.config import Config
from ..models.user import User
from ..serializers.common_serializer import default

import json

Config.connect()

class UserManager:

    @sync_to_async
    def create(self, user):
        """
        Create new user
        Parameters
        ----------
        user: dict
            User object to create
        """
        user = User(**user)
        result = user.save()
        return json.loads(result.to_json(), object_hook=default)

    @sync_to_async 
    def update(self, user_id, user):
        """
        Update a specific user
        Parameters
        ----------
        user_id: string
            The user ID to update
        user: dict
            User object to update
        """
        User.objects(id=ObjectId(user_id)).update_one(**user)
        updated_user = User.objects.get(id=ObjectId(user_id))
        updated_user.save()
        return json.loads(updated_user.to_json(), object_hook=default)

    @sync_to_async
    def delete(self, user_id):
        """
        Delete a specific user
        Parameters
        ----------
        user_id: string
            The user ID to delete
        """
        User.objects(id=ObjectId(user_id)).delete()
        return True