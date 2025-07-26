# chats/middleware.py
from datetime import datetime
import logging
from django.contrib.auth.models import AnonymousUser

logger = logging.getLogger(__name__)

class RequestLoggingMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        # Log the request before processing
        user = request.user if not isinstance(request.user, AnonymousUser) else "Anonymous"
        log_message = f"{datetime.now()} - User: {user} - Path: {request.path}"
        logger.info(log_message)

        # Process the request
        response = self.get_response(request)

        return response