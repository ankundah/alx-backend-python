from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.response import Response
from .models import Conversation, Message
from rest_framework.exceptions import PermissionDenied
from .serializers import (
    ConversationSerializer,
    MessageSerializer
)
from django.contrib.auth import get_user_model
from rest_framework.permissions import IsAuthenticated

User = get_user_model()

class ConversationViewSet(viewsets.ModelViewSet):
    serializer_class = ConversationSerializer
    permission_classes = [IsAuthenticated]
    queryset = Conversation.objects.prefetch_related('participants', 'messages')

    def get_serializer_class(self):
        if self.action == 'create':
            return ConversationSerializer
        return super().get_serializer_class()

    def get_queryset(self):
        """Return only conversations where current user is a participant"""
        return self.queryset.filter(participants=self.request.user)

    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        conversation = serializer.save()
        
        # Always add the current user as participant
        conversation.participants.add(request.user)
        
        # Return the full conversation details
        output_serializer = ConversationSerializer(conversation, context={'request': request})
        return Response(output_serializer.data, status=status.HTTP_201_CREATED)

    @action(detail=True, methods=['get'])
    def messages(self, request, pk=None):
        """Get all messages for a specific conversation"""
        conversation = self.get_object()
        messages = conversation.messages.all().order_by('sent_at')
        serializer = MessageSerializer(messages, many=True)
        return Response(serializer.data)

class MessageViewSet(viewsets.ModelViewSet):
    serializer_class = MessageSerializer
    permission_classes = [IsAuthenticated]
    queryset = Message.objects.select_related('sender', 'conversation')

    def get_queryset(self):
        """Return only messages in conversations where user is a participant"""
        return self.queryset.filter(
            conversation__participants=self.request.user
        ).order_by('-sent_at')

    def perform_create(self, serializer):
        """Automatically set the sender to the current user"""
        conversation = serializer.validated_data['conversation']
        if not conversation.participants.filter(id=self.request.user.id).exists():
            raise PermissionDenied("You're not a participant in this conversation")
        serializer.save(sender=self.request.user)
