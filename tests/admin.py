from django.contrib import admin
from .models import *

# Register your models here.

admin.site.register(Test)
admin.site.register(Task)
admin.site.register(AnswerOption)
admin.site.register(TypeOfTask)