from django.db import models
from django.contrib.auth.models import User
import random
from django.db.models.signals import post_save
from django.dispatch import receiver
# Create your models here.


class DirectMessage(models.Model):
    sender = models.ForeignKey(User, on_delete=models.DO_NOTHING, null=True, blank=True)
    to = models.ManyToManyField(User, related_name='to')
    title = models.CharField(max_length=255)
    body = models.TextField()
    slug = models.SlugField(default='', unique=True, blank=True, null=True)
    is_read = models.BooleanField(default=False)
    read_date = models.DateTimeField(null=True)
    date = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.sender.first_name} {self.sender.last_name} - {self.title}"


@receiver(post_save, sender=DirectMessage)
def post_save_direct_message(sender, instance, created, *args, **kwargs):
    if created:
        signs = "1234567890QWERTYUIOPASDFGHJKLZXCVBNMqwertyuiopasdfghjklzxcvbnm"
        code = ""
        for _ in range(30):
            code += signs[random.randint(0, len(signs) - 1)]

        while sender.objects.filter(slug=code):
            code = ""
            for _ in range(30):
                code += signs[random.randint(0, len(signs) - 1)]

        instance.slug = code
        instance.save()