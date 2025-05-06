# middleware.py
from django.utils import timezone
from .models import UserProfile
import datetime
from django.urls import resolve


class UserActivityMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        response = self.get_response(request)

        # Проверяем, является ли запрос запросом на переход между страницами
        current_path = resolve(request.path_info).url_name
        page_transition = current_path != 'update_user_status'

        if request.user.is_authenticated and page_transition:
            user_profile = request.user.userprofile
            user_profile.last_activity = timezone.now()
            user_profile.save()

        return response

    def user_is_active(self, last_activity):
        # Определите, когда пользователь считается активным
        # Например, если он был активен в течение последних 5 минут
        return timezone.now() - last_activity < datetime.timedelta(minutes=5)
