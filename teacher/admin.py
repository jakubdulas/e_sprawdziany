from django.contrib import admin
from .models import *

# Register your models here.

admin.site.register(School)
admin.site.register(Teacher)
admin.site.register(Class)
admin.site.register(Headmaster)
admin.site.register(Bell)
admin.site.register(SchoolTerm)
admin.site.register(SchoolYear)