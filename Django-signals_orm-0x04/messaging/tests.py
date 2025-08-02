from django.test import TestCase
from django.contrib.auth.models import User
from .models import Message, Notification, MessageHistory

class MessagingSignalTest(TestCase):

    def setUp(self):
        self.sender = User.objects.create_user(username='alice', password='pass')
        self.receiver = User.objects.create_user(username='bob', password='pass')

    def test_notification_created_on_message_send(self):
        msg = Message.objects.create(sender=self.sender, receiver=self.receiver, content='Hey Bob!')
        notifications = Notification.objects.filter(user=self.receiver, message=msg)
        self.assertEqual(notifications.count(), 1)

def test_edit_logs_history(self):
    msg = Message.objects.create(sender=self.sender, receiver=self.receiver, content='Hello')
    msg.content = 'Hello, again'
    msg.save()

    history = MessageHistory.objects.filter(message=msg)
    self.assertEqual(history.count(), 1)
    self.assertEqual(history.first().previous_content, 'Hello')
    self.assertTrue(msg.edited)

def test_user_deletion_cleans_up_data(self):
    user = User.objects.create_user(username="testuser", password="testpass")
    msg = Message.objects.create(sender=user, receiver=self.receiver, content="Test")
    notif = Notification.objects.create(user=user, message=msg, content="Notify")

    user.delete()

    self.assertFalse(Message.objects.filter(sender=user).exists())
    self.assertFalse(Notification.objects.filter(user=user).exists())
