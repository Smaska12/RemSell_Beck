# Файл: management/commands/update_user_activity.py

from django.core.management.base import BaseCommand
from main.models import UserProfile
from django.utils import timezone

class Command(BaseCommand):
    help = 'Обновляет статус активности пользователя'

    def handle(self, *args, **options):
        threshold = timezone.now() - timezone.timedelta(minutes=1)
        inactive_users = UserProfile.objects.filter(last_activity__lt=threshold)
        inactive_users.update(status='offline')
        self.stdout.write(self.style.SUCCESS('Успешно обновлен статус активности пользователей'))
