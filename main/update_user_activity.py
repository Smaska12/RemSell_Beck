import schedule
import time
from main.models import UserProfile
from django.utils import timezone

def update_user_status():
    threshold = timezone.now() - timezone.timedelta(minutes=1)
    inactive_users = UserProfile.objects.filter(last_activity__lt=threshold)
    inactive_users.update(status='offline')

# Расписание задачи: каждые 1 минуту
schedule.every(1).minutes.do(update_user_status)

while True:
    schedule.run_pending()
    time.sleep(1)
