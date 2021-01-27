from mongoengine import *
from mongoengine import signals

import datetime

class Todo(Document):
    title = StringField(required=True)
    description = StringField(required=True)
    done = BooleanField(required=False, default=False)
    user_id = ObjectIdField()
    created_at = DateTimeField(required=False, default=datetime.datetime.now())
    updated_at = DateTimeField(required=False, default=datetime.datetime.now())

    @classmethod
    def pre_save(cls, sender, document, **kwargs):
        """
        Executes before save the user
        """
        document.updated_at = datetime.datetime.now()

signals.pre_save.connect(Todo.pre_save, sender=Todo)