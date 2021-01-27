from django.conf.urls import url
from django.urls import path
from api.views import login_view, todo_view, user_view
from rest_framework.schemas import get_schema_view
from django.views.generic import TemplateView

urlpatterns = [
    url(r'^api/users/(?P<user_id>[a-f\d]{24})/todos$', todo_view.TodoList.as_view()),
    url(r'^api/users/(?P<user_id>[a-f\d]{24})/todos/(?P<todo_id>[a-f\d]{24})', todo_view.TodoDetail.as_view()),
    url(r'^api/users$', user_view.UserList.as_view()),
    url(r'^api/users/(?P<user_id>[a-f\d]{24})', user_view.UserDetail.as_view()),
    url(r'^api/auth/sign-in', login_view.Login.as_view()),
    path('docs/', TemplateView.as_view(
        template_name='documentation.html',
        extra_context={'schema_url':'openapi-schema'}
    ), name='swagger-ui'),
]