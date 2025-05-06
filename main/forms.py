from django import forms
from .models import Product, Rating, UserProfile, PaymentMethod, DeliveryMethod, Category
from django.contrib.auth.models import User

class ProductForm(forms.ModelForm):
    categories = forms.ModelMultipleChoiceField(
        queryset=Category.objects.all(),
        widget=forms.CheckboxSelectMultiple,  # Виджет для отображения чекбоксов
        required=False
    )

    class Meta:
        model = Product
        fields = ['name', 'description', 'quantity', 'image', 'categories', 'price']

    def __init__(self, *args, **kwargs):
        self.user = kwargs.pop('user', None)
        super(ProductForm, self).__init__(*args, **kwargs)

    def save(self, commit=True):
        instance = super(ProductForm, self).save(commit=False)
        instance.seller = self.user
        if commit:
            instance.save()
        return instance


class NotificationSettingsForm(forms.ModelForm):
    class Meta:
        model = User
        fields = ['email']

class SecuritySettingsForm(forms.ModelForm):
    class Meta:
        model = User
        fields = ['password']

class UpdateEmailForm(forms.Form):
    email = forms.EmailField()

    def clean_email(self):
        email = self.cleaned_data.get('email')
        if email:
            # Дополнительная проверка, если это необходимо
            return email
        else:
            raise forms.ValidationError("Введите корректный email адрес")

class UpdateUsernameForm(forms.Form):
    new_username = forms.CharField(max_length=150)

    def clean_new_username(self):
        new_username = self.cleaned_data.get('new_username')
        if not new_username:
            raise ValidationError("Please enter a new username.")
        return new_username

class AvatarForm(forms.ModelForm):
    class Meta:
        model = UserProfile
        fields = ['avatar']
        widgets = {
            'avatar': forms.FileInput(attrs={'class': 'form-control'}),
        }

class RatingForm(forms.ModelForm):
    class Meta:
        model = Rating
        fields = ['product', 'value', 'review', 'image']


class BioForm(forms.ModelForm):
    class Meta:
        model = UserProfile
        fields = ['bio']


class CheckoutForm(forms.Form):
    first_name = forms.CharField(label='Имя', max_length=50)
    last_name = forms.CharField(label='Фамилия', max_length=50)
    patronymic = forms.CharField(label='Отчество', max_length=50)
    email = forms.EmailField(label='Email')
    phone_number = forms.CharField(label='Номер телефона', max_length=15)
    # address = forms.CharField(label='Адрес доставки', widget=forms.Textarea)
    payment_method = forms.ModelChoiceField(label='Способ оплаты', queryset=PaymentMethod.objects.all())
    delivery_method = forms.ModelChoiceField(label='Способ доставки', queryset=DeliveryMethod.objects.all())
    quantity = forms.IntegerField(label='Количество', min_value=1)