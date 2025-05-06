from django import forms
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.models import User
from django.core.exceptions import ValidationError
from django.utils.translation import gettext_lazy as _

class UserRegistrationForm(UserCreationForm):
    email = forms.EmailField()

    class Meta:
        model = User
        fields = ['username', 'email', 'password1', 'password2']

    def clean_email(self):
        email = self.cleaned_data['email']
        domain = email.split('@')[1]
        allowed_domains = ['mail.ru', 'gmail.com']  # Список допустимых доменов
        if domain not in allowed_domains:
            raise ValidationError(_('Данный домен почтового ящика не поддерживается. Используемые домены: mail.ru и gmail.com'))
        return email

    def clean_username(self):
        username = self.cleaned_data.get('username')
        if username:
            return username.lower()
        return username

    def clean(self):
        cleaned_data = super().clean()
        email = cleaned_data.get('email')
        if email:
            self.clean_email()
        return cleaned_data