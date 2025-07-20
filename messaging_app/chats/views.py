from django_filters import rest_framework as filters
from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.exceptions import PermissionDenied
from .models import Conversation, Message
from .serializers import ConversationSerializer, MessageSerializer
from django.contrib.auth import get_user_model
from rest_framework.permissions import IsAuthenticated
from django.shortcuts import get_object_or_404

User = get_user_model()

# Add these filter classes
class ConversationFilter(filters.FilterSet):
    created_after = filters.DateTimeFilter(field_name='created_at', lookup_expr='gte')
    has_unread = filters.BooleanFilter(method='filter_has_unread')

    class Meta:
        model = Conversation
        fields = ['participants']

    def filter_has_unread(self, queryset, name, value):
        if value:
            return queryset.filter(messages__read=False).exclude(messages__sender=self.request.user)
        return queryset

class MessageFilter(filters.FilterSet):
    before = filters.DateTimeFilter(field_name='sent_at', lookup_expr='lte')
    after = filters.DateTimeFilter(field_name='sent_at', lookup_expr='gte')
    unread = filters.BooleanFilter(field_name='read')

    class Meta:
        model = Message
        fields = ['conversation', 'sender']

# Update the viewsets
class ConversationViewSet(viewsets.ModelViewSet):
    serializer_class = ConversationSerializer
    permission_classes = [IsAuthenticated]
    queryset = Conversation.objects.prefetch_related('participants', 'messages')
    filter_backends = [filters.DjangoFilterBackend]
    filterset_class = ConversationFilter

    def get_queryset(self):
        queryset = super().get_queryset()
        return queryset.filter(participants=self.request.user).distinct()

    @action(detail=True, methods=['get'])
    def messages(self, request, pk=None):
        conversation = self.get_object()
        messages = conversation.messages.all().order_by('sent_at')
        
        # Apply filtering to nested messages endpoint
        filtered_messages = MessageFilter(
            request.query_params,
            queryset=messages
        ).qs
        
        page = self.paginate_queryset(filtered_messages)
        if page is not None:
            serializer = MessageSerializer(page, many=True)
            return self.get_paginated_response(serializer.data)
            
        serializer = MessageSerializer(filtered_messages, many=True)
        return Response(serializer.data)

class MessageViewSet(viewsets.ModelViewSet):
    serializer_class = MessageSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        # For nested route: /conversations/<id>/messages/
        if 'conversation_pk' in self.kwargs:
            return Message.objects.filter(
                conversation_id=self.kwargs['conversation_pk'],
                conversation__participants=self.request.user
            ).order_by('-sent_at')
        
        # For flat route: /messages/
        return Message.objects.filter(
            conversation__participants=self.request.user
        ).order_by('-sent_at')

    def perform_create(self, serializer):
        # Handle both nested and flat creation
        if 'conversation_pk' in self.kwargs:
            conversation_id = self.kwargs['conversation_pk']
            conversation = get_object_or_404(
                Conversation,
                pk=conversation_id,
                participants=self.request.user
            )
            serializer.save(conversation=conversation, sender=self.request.user)
        else:
            conversation = serializer.validated_data['conversation']
            if not conversation.participants.filter(id=self.request.user.id).exists():
                raise PermissionDenied("Not a conversation participant")
            serializer.save(sender=self.request.user)