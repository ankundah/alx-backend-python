def build_thread(message):
    return {
        'id': message.id,
        'sender': message.sender.username,
        'receiver': message.receiver.username,
        'content': message.content,
        'timestamp': message.timestamp,
        'replies': [build_thread(reply) for reply in message.replies.all()]
    }
