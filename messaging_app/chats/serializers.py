from rest_framework import serializers
from .models import User, Conversation, Message
from django.contrib.auth.hashers import make_password
from rest_framework.exceptions import ValidationError

class UserSerializer(serializers.ModelSerializer):
    # Using SerializerMethodField for computed fields
    full_name = serializers.SerializerMethodField()
    role_display = serializers.SerializerMethodField()
    
    class Meta:
        model = User
        fields = [
            'user_id',
            'email',
            'first_name',
            'last_name',
            'full_name',  # Computed field
            'phone_number',
            'role',
            'role_display',  # Computed field
            'created_at'
        ]
        extra_kwargs = {
            'password_hash': {'write_only': True},
            'created_at': {'read_only': True},
            'role': {'write_only': True}  # Only show display version
        }

    def get_full_name(self, obj):
        return f"{obj.first_name} {obj.last_name}"

    def get_role_display(self, obj):
        return obj.get_role_display()

    def validate_phone_number(self, value):
        # Using CharField validation
        if value and not value.startswith('+'):
            raise ValidationError("Phone number must include country code (e.g., +1)")
        return value

class MessageSerializer(serializers.ModelSerializer):
    # Using CharField for custom message validation
    message_body = serializers.CharField(
        max_length=2000,
        error_messages={
            'max_length': "Message cannot exceed 2000 characters"
        }
    )
    sender_email = serializers.SerializerMethodField()

    class Meta:
        model = Message
        fields = [
            'message_id',
            'sender',
            'sender_email',
            'message_body',
            'sent_at'
        ]
        read_only_fields = ['message_id', 'sent_at', 'sender']

    def get_sender_email(self, obj):
        return obj.sender.email

    def validate(self, data):
        if len(data.get('message_body', '').strip()) < 1:
            raise ValidationError("Message cannot be empty")
        return data

class ConversationSerializer(serializers.ModelSerializer):
    # Using CharField for participant emails
    participant_emails = serializers.ListField(
        child=serializers.CharField(max_length=255),
        write_only=True,
        required=False
    )
    last_message = serializers.SerializerMethodField()
    unread_count = serializers.SerializerMethodField()

    class Meta:
        model = Conversation
        fields = [
            'conversation_id',
            'participants',
            'participant_emails',
            'messages',
            'last_message',
            'unread_count',
            'created_at'
        ]
        read_only_fields = ['conversation_id', 'created_at']

    def get_last_message(self, obj):
        last_msg = obj.messages.last()
        return MessageSerializer(last_msg).data if last_msg else None

    def get_unread_count(self, obj):
        request = self.context.get('request')
        if request and request.user.is_authenticated:
            return obj.messages.exclude(sender=request.user).count()
        return 0

    def validate_participant_emails(self, value):
        if len(value) < 1:
            raise serializers.ValidationError("At least one participant is required")
        return value