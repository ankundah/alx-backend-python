from rest_framework import serializers
from .models import User, Conversation, Message
from django.contrib.auth.hashers import make_password

class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = [
            'user_id', 
            'email',
            'first_name',
            'last_name',
            'phone_number',
            'role',
            'created_at'
        ]
        extra_kwargs = {
            'password_hash': {'write_only': True},
            'created_at': {'read_only': True}
        }

    def create(self, validated_data):
        # Hash password before saving
        validated_data['password_hash'] = make_password(validated_data.get('password_hash', ''))
        return super().create(validated_data)

class MessageSerializer(serializers.ModelSerializer):
    sender = UserSerializer(read_only=True)
    
    class Meta:
        model = Message
        fields = [
            'message_id',
            'sender',
            'message_body',
            'sent_at'
        ]
        read_only_fields = ['message_id', 'sent_at']

class ConversationSerializer(serializers.ModelSerializer):
    participants = UserSerializer(many=True, read_only=True)
    messages = MessageSerializer(many=True, read_only=True)
    
    class Meta:
        model = Conversation
        fields = [
            'conversation_id',
            'participants',
            'messages',
            'created_at'
        ]
        read_only_fields = ['conversation_id', 'created_at']

    def create(self, validated_data):
        # Handle participant addition through separate endpoint
        conversation = Conversation.objects.create()
        return conversation

class ConversationCreateSerializer(serializers.ModelSerializer):
    participant_emails = serializers.ListField(
        child=serializers.EmailField(),
        write_only=True
    )
    
    class Meta:
        model = Conversation
        fields = ['participant_emails']
        
    def create(self, validated_data):
        emails = validated_data.pop('participant_emails')
        conversation = Conversation.objects.create()
        
        # Add participants by email
        for email in emails:
            try:
                user = User.objects.get(email=email)
                conversation.participants.add(user)
            except User.DoesNotExist:
                continue
                
        return conversation