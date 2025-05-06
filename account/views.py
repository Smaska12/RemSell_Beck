from django.contrib.auth import authenticate, login
from django.contrib import messages

from .forms import UserRegistrationForm
from django.shortcuts import render, redirect
from django.http import JsonResponse
from main.models import Category
# from ..main.models import Category

def reg(request):
    categories = Category.objects.all()
    if request.method == 'POST':
        form = UserRegistrationForm(request.POST)
        if form.is_valid():
            user = form.save()
            username = form.cleaned_data.get('username')
            login(request, user)  # Автоматический вход после успешной регистрации
            messages.success(request, f'Аккаунт для {username} был успешно создан и вы вошли в систему!')
            return redirect('log')
    else:
        form = UserRegistrationForm()

    # Если метод запроса GET или форма не валидна, передаем форму с возможными ошибками в шаблон
    return render(request, 'account/reg.html', {'form': form, 'categories': categories})

def entry(request):
    categories = Category.objects.all()
    if request.method == 'POST':
        username = request.POST.get('username')
        password = request.POST.get('password')
        user = authenticate(request, username=username, password=password)
        if user is not None:
            login(request, user)
            return JsonResponse({'success': True})  # Отправляем JSON-ответ об успешном входе
        else:
            return JsonResponse({'success': False, 'error_message': 'Неверное имя пользователя или пароль'})  # Отправляем JSON-ответ с сообщением об ошибке
    else:
        return render(request, 'account/entry.html', {'categories': categories})

