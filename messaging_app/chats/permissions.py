# chats/permissions.py
from rest_framework.permissions import BasePermission, IsAuthenticated
from .models import Conversation, Message

class IsParticipantOfConversation(IsAuthenticated):
    
    def has_object_permission(self, request, view, obj):
        # First check if user is authenticated (parent class check)
        if not super().has_permission(request, view):
            return False

        # Handle Conversation objects
        if isinstance(obj, Conversation):
            return obj.participants.filter(id=request.user.id).exists()
        
        # Handle Message objects
        elif isinstance(obj, Message):
            return obj.conversation.participants.filter(id=request.user.id).exists()
        
        # For list views or other objects, just require authentication
        return True