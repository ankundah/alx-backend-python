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
from .permissions import IsParticipantOfConversation
from django.views.decorators.cache import cache_page


User = get_user_model()

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

@cache_page(60)
class ConversationViewSet(viewsets.ModelViewSet):
    serializer_class = ConversationSerializer
    permission_classes = [IsParticipantOfConversation] 
    filter_backends = [filters.DjangoFilterBackend]
    filterset_class = ConversationFilter

    def get_queryset(self):
        return Conversation.objects.filter(
            participants=self.request.user
        ).prefetch_related('participants', 'messages').distinct()

    def perform_create(self, serializer):
        """Automatically add creator as participant"""
        conversation = serializer.save()
        conversation.participants.add(self.request.user)

    @action(detail=True, methods=['get'])
    def messages(self, request, pk=None):
        """Get messages with nested filtering"""
        conversation = self.get_object()
        messages = MessageFilter(
            request.query_params,
            queryset=conversation.messages.all()
        ).qs.order_by('sent_at')
        
        page = self.paginate_queryset(messages)
        serializer = MessageSerializer(page if page is not None else messages, many=True)
        return self.get_paginated_response(serializer.data) if page else Response(serializer.data)

class MessageViewSet(viewsets.ModelViewSet):
    serializer_class = MessageSerializer
    permission_classes = [IsParticipantOfConversation] 
    filter_backends = [filters.DjangoFilterBackend]
    filterset_class = MessageFilter

    def get_queryset(self):
        base_qs = Message.objects.filter(
            conversation__participants=self.request.user
        ).select_related('sender', 'conversation')
        
        if 'conversation_pk' in self.kwargs:
            return base_qs.filter(
                conversation_id=self.kwargs['conversation_pk']
            )
        return base_qs

    def perform_create(self, serializer):
        """Handle message creation with security checks"""
        if 'conversation_pk' in self.kwargs:
            conversation = get_object_or_404(
                Conversation,
                pk=self.kwargs['conversation_pk'],
                participants=self.request.user
            )
            serializer.save(conversation=conversation, sender=self.request.user)
        else:
            conversation = serializer.validated_data['conversation']
            if not conversation.participants.filter(id=self.request.user.id).exists():
                raise PermissionDenied("Not a conversation participant")
            serializer.save(sender=self.request.user)
    
    def destroy(self, request, *args, **kwargs):
        try:
            instance = self.get_object()
            self.perform_destroy(instance)
            return Response(status=status.HTTP_204_NO_CONTENT)
        except PermissionDenied:
            return Response(
                {"detail": "You don't have permission to delete this message"},
                status=status.HTTP_403_FORBIDDEN
            )

    @action(detail=True, methods=['put', 'patch'])
    def mark_as_read(self, request, pk=None):
        message = self.get_object()
        if not message.conversation.participants.filter(id=request.user.id).exists():
            return Response(
                {"detail": "You're not a participant in this conversation"},
                status=status.HTTP_403_FORBIDDEN
            )
        message.read = True
        message.save()
        return Response({'status': 'message marked as read'})