from django.test import TestCase
from django.contrib.auth.models import User
from .models import Message, Notification

class MessagingSignalTest(TestCase):

    def setUp(self):
        self.sender = User.objects.create_user(username='alice', password='pass')
        self.receiver = User.objects.create_user(username='bob', password='pass')

    def test_notification_created_on_message_send(self):
        msg = Message.objects.create(sender=self.sender, receiver=self.receiver, content='Hey Bob!')
        notifications = Notification.objects.filter(user=self.receiver, message=msg)
        self.assertEqual(notifications.count(), 1)
