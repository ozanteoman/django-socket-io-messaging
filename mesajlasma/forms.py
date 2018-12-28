from django import forms
from django.contrib.auth.models import User


class NewMessageForm(forms.Form):
    to = forms.CharField(required=True, max_length=100, min_length=1)
    message = forms.CharField(required=True, widget=forms.Textarea, min_length=1)

    def __init__(self, *args, **kwargs):
        self.request = kwargs.pop('request')
        super(NewMessageForm, self).__init__(*args, **kwargs)
        for field in self.fields:
            self.fields[field].widget.attrs.update({'class': 'form-control'})

        self.fields['message'].widget.attrs.update({'placeholder':'Bir şeyler yazınız.'})
        self.fields['to'].widget.attrs.update({'placeholder':'Bir Kullanıcı Arayın.'})

    def clean_to(self):
        value = self.cleaned_data.get('to')
        user = User.objects.filter(username=value).exclude(username=self.request.user.username)
        if not user.exists():
            raise forms.ValidationError('Lütfen Geçerli Bir Kullanıcı Seçiniz.')

        return user.first()