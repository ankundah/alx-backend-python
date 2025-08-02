from django.contrib.auth.decorators import login_required
from django.shortcuts import redirect
from django.contrib.auth import get_user_model
from django.http import JsonResponse
from .models import Message
from .utils import build_thread  

@login_required
def delete_user(request):
    user = request.user
    user.delete()
    return redirect('account_deleted')  

def get_message_thread(request, message_id):
    try:
        message = Message.objects.select_related('sender', 'receiver') \
            .prefetch_related('replies__replies__replies') \
            .get(id=message_id, parent_message__isnull=True)
        
        thread = build_thread(message)
        return JsonResponse(thread, safe=False)
    except Message.DoesNotExist:
        return JsonResponse({'error': 'Message not found'}, status=404)

@login_required
def unread_inbox(request):
    user = request.user
    unread_messages = Message.unread.for_user(user)
    
    data = [{
        "id": msg.id,
        "sender": msg.sender.username,
        "content": msg.content,
        "timestamp": msg.timestamp,
    } for msg in unread_messages]

    return JsonResponse(data, safe=False)