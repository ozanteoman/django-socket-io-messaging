from django.template.loader import render_to_string
from django.shortcuts import render, reverse, HttpResponseRedirect, get_object_or_404, HttpResponse
from django.contrib.auth.models import User
from django.http import JsonResponse

from .models import Mesaj
from .forms import NewMessageForm
from .decorators import ajax_required


def index(request):
    return HttpResponseRedirect(reverse('messages:inbox'))


def inbox(request):
    conversations = Mesaj.get_conversations(request.user)
    active_conversation = None
    messages = None
    if conversations:
        conversation = conversations[0]
        active_conversation = conversation['user'].username
        messages = Mesaj.objects.filter(user=request.user, conversation=conversation['user'])
        messages.update(is_read=True)
        for conversation in conversations:
            # bu kısımlar fonksiyon olur tekrar ediyor.
            if conversation['user'].username == active_conversation:
                conversation['unread'] = 0
            elif conversation['unread'] == 0:
                conversation['last_text'] = conversation['last_text']
            else:
                conversation['last_text'] = '<b style="color:black">' + conversation['last_text'] + '</b>'
        # en son konuşmanın okunmama sayısını 0 yaptık.

    return render(request, 'inbox.html', {
        'msgs': messages,
        'conversations': conversations,
        'active': active_conversation
    })


def new_message(request):
    form = NewMessageForm(request=request, data=request.POST or None)
    if request.is_ajax():
        if form.is_valid():
            to_user = form.cleaned_data.get('to')
            message = form.cleaned_data.get('message')
            sended_message = Mesaj.send_message(from_user=request.user, to_user=to_user, message=message)

            conversations = Mesaj.get_conversations(request.user)  # konuşma listesini güncellemek için getirdik.
            # yukaridaki kısım mesajı gönderen kullanıcıların bilgilerini güncellemek için

            # konuşmaları güncellemek için yaptık.
            conversations_html = render_to_string('include/partial_conversations.html',
                                                  context={'conversations': conversations,
                                                           'active': None}, request=request)
            new_message_html = render_to_string('include/each_message.html', request=request,
                                                context={'msg': sended_message})
            new_message_alici = render_to_string('include/each_message.html', context={'msg': sended_message})
            return JsonResponse(
                data={'return_url':reverse('messages:inbox'),'new_message_alici': new_message_alici, 'to_user': to_user.username, 'msg': message,
                      'conversations_html': conversations_html, 'new_message_html': new_message_html})

    conversations = Mesaj.get_conversations(user=request.user)
    for conversation in conversations:
        if conversation['unread'] != 0:
            last_text = conversation['last_text']
            conversation['last_text'] = '<b style="color:black">' + last_text + '</b>'

    return render(request, 'new_message.html', context={'conversations': conversations, 'form': form})


@ajax_required
def send_message(request, username):
    message = request.GET.get('message', '')
    if len(message.strip()) == 0:
        # eğer gelen mesaj boşsa geriye boş değer göndermek için
        # javascript ile kontrol ediliyor fakat her ihtimala karşı.
        return HttpResponse()
    to_user = get_object_or_404(User, username=username)
    from_user = request.user
    sended_message = Mesaj.send_message(from_user=from_user, to_user=to_user, message=message)
    conversations = Mesaj.get_conversations(request.user)  # konuşma listesini güncellemek için getirdik.
    active_conversation = conversations[0]['user'].username
    # yukaridaki kısım mesajı gönderen kullanıcıların bilgilerini güncellemek için

    # konuşmaları güncellemek için yaptık.
    conversations_html = render_to_string('include/partial_conversations.html',
                                          context={'conversations': conversations,
                                                   'active': active_conversation}, request=request)
    new_message_html = render_to_string('include/each_message.html', request=request, context={'msg': sended_message})
    new_message_alici = render_to_string('include/each_message.html', context={'msg': sended_message})
    return JsonResponse(data={'new_message_alici': new_message_alici, 'to_user': to_user.username, 'msg': message,
                              'conversations_html': conversations_html, 'new_message_html': new_message_html})


@ajax_required
def get_conversations_after_new_message(request, active_username):
    # active_username , - > aktif o an mesajlaştığım kullanıcı
    # buradaki amaç mesaj geldikten sonra sol pencereki konuşmaları güncellemek için
    # mesaj bir üstteki fonksiyon tarafından ekrana basılıyor.
    # konuşma ise bu ekran tarafından.
    active_user = get_object_or_404(User, username=active_username)  # basitten doğruluğunu kontrol etmek için
    Mesaj.signed_as_read_message(request.user, active_user)  # aktif mesajı okundu olarak gösteriyoruz.
    conversations = Mesaj.get_conversations(request.user)

    for conversation in conversations:
        if conversation['user'].username != active_user.username and conversation['unread'] != 0:
            last_text = conversation['last_text']
            conversation['last_text'] = '<b style="color:black">' + last_text + '</b>'
            # aktif konuşmanın olmadığı yerlerde son mesajı bold yaptık.
    conversations_html = render_to_string('include/partial_conversations.html',
                                          context={'conversations': conversations,
                                                   'active': active_user.username}, request=request)
    return JsonResponse(data={'conversations_html': conversations_html})


@ajax_required
def get_conversations_when_star_new_conversation(request):
    # bu fonksyion new_message url adresnde olduğumuzda çalışacak link
    # yeni mesaj geldiğinde konuşmada belirgin olsun diye.
    # yukarıdaki fonksyion ile çok benzer bunun için ortak fonksyionlar
    # yazabilirdik fakat bu kısımlar size kalmış arkadaşlar
    conversations = Mesaj.get_conversations(request.user)
    for conversation in conversations:
        if conversation['unread'] != 0:
            last_text = conversation['last_text']
            conversation['last_text'] = '<b style="color:black">' + last_text + '</b>'

    conversations_html = render_to_string('include/partial_conversations.html',
                                          context={'conversations': conversations,
                                                   'active': None}, request=request)
    return JsonResponse(data={'conversations_html': conversations_html})


def messages(request, username):
    conversations = Mesaj.get_conversations(user=request.user)
    active_conversation = username
    messages = Mesaj.objects.filter(user=request.user, conversation__username=username)
    messages.update(is_read=True)
    for conversation in conversations:
        if conversation['user'].username == username:
            conversation['unread'] = 0
            conversation['last_text'] = conversation['last_text']
        elif conversation['unread'] == 0:
            conversation['last_text'] = conversation['last_text']
        else:
            conversation['last_text'] = '<b style="color:black">' + conversation['last_text'] + '</b>'
    return render(request, 'inbox.html', {
        'msgs': messages,
        'conversations': conversations,
        'active': active_conversation
    })


def user_search(request):
    users_list = []
    username = request.GET.get('to', None)
    users_query = User.objects.filter(username__icontains=username).exclude(username=request.user.username)
    # exclude kendisine mesaj atmasın diye.
    for user in users_query:
        data = {'username': user.username, }
        users_list.append(data)

    return JsonResponse(data={'users_list': users_list})
