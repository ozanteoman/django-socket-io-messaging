from django.db import models

from django.contrib.auth.models import User


class Mesaj(models.Model):
    user = models.ForeignKey(User, related_name='+', verbose_name='User')
    message = models.TextField(max_length=1000, blank=True, verbose_name='Message')
    date = models.DateTimeField(auto_now_add=True, verbose_name='Date')
    conversation = models.ForeignKey(User, related_name='+', verbose_name='Conversation')
    from_user = models.ForeignKey(User, related_name='+', verbose_name='From')
    is_read = models.BooleanField(default=False, verbose_name='is Read')

    class Meta:
        verbose_name_plural = 'Messages'
        ordering = ['date']

    def __str__(self):
        return self.message

    def get_date_and_hour(self):
        time = self.date.strftime("%I:%M %p")
        date = self.date.strftime("%B %d")
        new_value = "{0} | {1}".format(time, date)
        return new_value

    @staticmethod
    def signed_as_read_message(user, conversation):
        #eğer o anki konuşma ise direk okundu yapıyoruz.
        un_readed_messages = Mesaj.objects.filter(user=user, conversation=conversation, is_read=False)
        un_readed_messages.update(is_read=True)

    @staticmethod
    def send_message(from_user, to_user, message):
        message = message[:1000]
        current_user_message = Mesaj(message=message,
                                     user=from_user,
                                     from_user=from_user,
                                     conversation=to_user,
                                     is_read=True)
        current_user_message.save()
        Mesaj(from_user=from_user,
              conversation=from_user,
              user=to_user,
              message=message).save()

        return current_user_message

    @staticmethod
    def last_message_text_bold_or_normal(last_message, user, index):
        # eğer gelen mesaj karşı taraftan geldiyse ve okunmamışsa bold göstermek için
        if index != 0 and last_message.from_user != user and last_message.is_read == False:
            return "<b style='color:black'>{0}</b>".format(last_message.message)
        return last_message.message

    @staticmethod
    def get_conversations(user):
        conversations = Mesaj.objects.filter(user=user).values('conversation').annotate(
            last=models.Max('date')).order_by('-last')
        users = []
        for conversation in conversations:
            last_message = \
                Mesaj.objects.filter(user=user, conversation__pk=conversation['conversation']).order_by('-date')[0]
            users.append({
                'user': User.objects.get(pk=conversation['conversation']),
                'last': conversation['last'],
                'unread': Mesaj.objects.filter(user=user, conversation__pk=conversation['conversation'],
                                               is_read=False).count(),
                'last_message': last_message,
                'last_text': last_message.message
            })

        return users
