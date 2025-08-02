from django.urls import path
from messaging.views import delete_user, get_message_thread

urlpatterns = [
    path('delete-account/', delete_user, name='delete_user'),
    path('api/messages/<int:message_id>/thread/', get_message_thread),
]
