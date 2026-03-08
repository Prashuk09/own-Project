from notifications.models import Notification

def create_notification(user, title, message, link=None):

    Notification.objects.create(
        user=user,
        title=title,
        message=message,
        link=link
    )