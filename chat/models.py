from django.db import models
from django.utils import timezone
import uuid

class AnonymousRoom(models.Model):
    room_name = models.UUIDField(default=uuid.uuid4, editable=False, unique=True)
    ip_address = models.CharField(max_length=45)
    start_time = models.DateTimeField(default=timezone.now)

    def __str__(self):
        return str(self.room_name)

class AnonymousRoomMessage(models.Model):
    SENDER_CHOICES = (
        ('ANONYMOUS', 'Anonymous'),
        ('ADMIN', 'Admin'),
    )

    room = models.ForeignKey(AnonymousRoom, related_name='messages', on_delete=models.CASCADE)
    message = models.TextField()
    sender_type = models.CharField(max_length=10, choices=SENDER_CHOICES)
    sent_time = models.DateTimeField(default=timezone.now)
    read = models.BooleanField(default=False)

    def __str__(self):
        return f'Message in {self.room.room_name} from {self.get_sender_type_display()}'
