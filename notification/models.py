from django.db import models

# Create your models here.
from django.db import models
from django.contrib.auth.models import User

class Notification(models.Model):
    # Choices for notification types
    USER_NOTIFICATION = 'user'
    SYSTEM_NOTIFICATION = 'system'
    ALERT_NOTIFICATION = 'alert'
    MESSAGE_NOTIFICATION = 'message'
    BILL_NOTIFICATION = 'bill'
    
    NOTIFICATION_CHOICES = [
        (USER_NOTIFICATION, 'User Notification'),
        (SYSTEM_NOTIFICATION, 'System Notification'),
        (ALERT_NOTIFICATION, 'Alert Notification'),
        (MESSAGE_NOTIFICATION, 'Message Notification'),
        (BILL_NOTIFICATION, 'Bill Notification'),
    ]
    
    recipient = models.ForeignKey(User, on_delete=models.CASCADE)
    message = models.TextField()
    timestamp = models.DateTimeField(auto_now_add=True)
    read = models.BooleanField(default=False)
    notification_type = models.CharField(max_length=50, choices=NOTIFICATION_CHOICES)

    class Meta:
        ordering = ['-timestamp']

    def __str__(self):
        return f"{self.recipient.username}: {self.message}"
