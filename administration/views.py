from django.shortcuts import render
from django.http import HttpResponse
from .decorators import *


@superuser_only
def home(request):
    return HttpResponse('hello admin!')