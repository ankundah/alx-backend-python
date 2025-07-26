from rest_framework.permissions import BasePermission
from rest_framework import status
from django.http import HttpResponseForbidden
from .models import Conversation, Message

class IsParticipantOfConversation(BasePermission):
    message = "You are not a participant of this conversation"
    code = status.HTTP_403_FORBIDDEN

    def has_permission(self, request, view):
        # First check if user is authenticated
        if not request.user.is_authenticated:
            return False

        # For list/create views, just require authentication
        if view.action in ['list', 'create']:
            return True

        return True  # Object permission will be checked in has_object_permission

    def has_object_permission(self, request, view, obj):
        # Check conversation participation for all methods
        if isinstance(obj, Conversation):
            is_participant = obj.participants.filter(id=request.user.id).exists()
        elif isinstance(obj, Message):
            is_participant = obj.conversation.participants.filter(id=request.user.id).exists()
        else:
            is_participant = False

        # Special handling for different HTTP methods
        if request.method in ['GET', 'HEAD', 'OPTIONS']:
            return is_participant
        elif request.method in ['PUT', 'PATCH', 'DELETE']:
            # For modifications, ensure user is participant AND owns the message (if applicable)
            if isinstance(obj, Message):
                return is_participant and obj.sender == request.user
            return is_participant
        return False