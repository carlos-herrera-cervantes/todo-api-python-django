from mongoengine import *
from mongoengine import signals

from ..models.roles import Role

import datetime
import bcrypt

class User(Document):
    email = EmailField(required=True)
    first_name = StringField(required=True)
    last_name = StringField(required=True)
    password = StringField(required=True)
    role = StringField(required=False, default=Role.CLIENT.value)
    todos = ListField(required=False)
    created_at = DateTimeField(required=False, default=datetime.datetime.now())
    updated_at = DateTimeField(required=False, default=datetime.datetime.now())

    @classmethod
    def pre_save(cls, sender, document, **kwargs):
        """
        Executes before save the user
        """
        document.updated_at = datetime.datetime.now()

    @classmethod
    def post_save(cls, sender, document, **kwargs):
        is_new = kwargs.get('created')

        if not is_new:
            return

        password = document.password.encode('utf-8')
        hashed_password = bcrypt.hashpw(password, bcrypt.gensalt())
        document.password = hashed_password.decode('utf-8')
        document.save()

signals.pre_save.connect(User.pre_save, sender=User)
signals.post_save.connect(User.post_save, sender=User)