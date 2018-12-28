from django.conf.urls import url
from .views import inbox, new_message, user_search, messages, send_message, get_conversations_after_new_message, \
    get_conversations_when_star_new_conversation

urlpatterns = [
    url(r'^$', inbox, name='inbox'),
    url(r'^new-message$', new_message, name='new-message'),
    url(r'^users-search$', user_search, name='user-search'),
    url(r'^send-message/(?P<username>[\w.@+-]+)/$', send_message, name='send-message'),
    url(r'^get-conversations-when-star-new-conversation/$', get_conversations_when_star_new_conversation,
        name='get-conversations-when-star-new-conversation'),
    url(r'^get-conversations-after-new-message/(?P<active_username>[\w.@+-]+)/$', get_conversations_after_new_message,
        name='get-conversations-after-new-message'),
    url(r'^(?P<username>[\w.@+-]+)$', messages, name='messages')
]
