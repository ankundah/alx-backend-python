from rest_framework.permissions import BasePermission
from rest_framework import permissions

class IsConversationParticipant(BasePermission):
    def has_object_permission(self, request, view, obj):
        # For Conversation objects
        if hasattr(obj, 'participants'):
            return request.user in obj.participants.all()
        # For Message objects
        elif hasattr(obj, 'conversation'):
            return request.user in obj.conversation.participants.all()
        return False