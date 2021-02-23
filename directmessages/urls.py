from django.urls import path
from .views import *


urlpatterns = [
    path('nowa-wiadomosc/', new_message, name='send_message'),
    path('wszyskie/', messages_list, name='messages_list'),
    path('w/<slug:dm_slug>/', message_details, name='message_details'),
    path('odpowiedz/<int:user_id>/<slug:dm_slug>/', respond_to_message, name='respond_to_message'),
    path('wyslane/', sent_messages, name='sent_messages'),
]