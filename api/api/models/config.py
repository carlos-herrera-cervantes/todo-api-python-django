from mongoengine import connect

class Config:
    
    @staticmethod
    def connect():
        connect('todo-api-django')