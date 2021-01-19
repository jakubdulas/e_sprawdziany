from django.db import models
from django.contrib.auth.models import User
import random
# Create your models here.


class DirectMessage(models.Model):
    sender = models.ForeignKey(User, on_delete=models.DO_NOTHING, null=True, blank=True)
    to = models.ManyToManyField(User, related_name='to')
    title = models.CharField(max_length=255)
    body = models.TextField()
    slug = models.SlugField(default='', unique=True, blank=True, null=True)
    is_read = models.BooleanField(default=False)
    date = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.sender.first_name} {self.sender.last_name} - {self.title}"

    def save(self, *args, **kwargs):
        signs = [str(i) for i in range(10)]
        letters = 'abcdefghijklmnopqrstuvwxyzQWERTYUIOPASDFGHJKLZXCVBNM'
        code = ''
        for letter in letters:
            signs.append(letter)

        for i in range(45):
            letter = random.choice(signs)
            code += letter

        while DirectMessage.objects.filter(slug=code):
            code = ''
            for i in range(45):
                letter = random.choice(signs)
                code += letter

        self.slug = code

        super(DirectMessage, self).save(*args, **kwargs)