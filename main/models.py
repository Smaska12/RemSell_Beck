from django.db import models
from django.db.models.signals import pre_save, post_save, post_delete, pre_delete
from django.dispatch import receiver
from django.contrib.auth.models import User
from django.db.models import Count, Q, Avg
from decimal import Decimal
from django.urls import reverse
from django.utils import timezone


# Часть продукта
class Category(models.Model):
    name = models.CharField(max_length=100)

    def __str__(self):
        return self.name


class Product(models.Model):
    name = models.CharField(max_length=100)
    description = models.TextField(max_length=1000)
    quantity = models.PositiveIntegerField(default=0)
    price = models.DecimalField(max_digits=10, decimal_places=2, default=0.00)
    image = models.ImageField(upload_to='products/', default='products/default_product_image.jpg')
    seller = models.ForeignKey(User, on_delete=models.CASCADE, default=None)
    categories = models.ManyToManyField(Category, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    rating = models.DecimalField(max_digits=3, decimal_places=2, default=0.00)
    available = models.BooleanField(default=True)

    def get_absolute_url(self):
        return reverse('product_detail', args=[str(self.id)])

    def __str__(self):
        return self.name

@receiver(pre_save, sender=Product)
def check_product_availability(sender, instance, **kwargs):
    if instance.quantity == 0:
        instance.available = False
    else:
        instance.available = True

@receiver(pre_save, sender=Product)
def set_seller_default(sender, instance, **kwargs):
    if not instance.seller:
        instance.seller = instance.request.user


class Rating(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='ratings')
    product = models.ForeignKey(Product, on_delete=models.SET_NULL, related_name='ratings', null=True, blank=True)
    seller = models.ForeignKey(User, on_delete=models.CASCADE, related_name='seller_ratings', default=None)
    value = models.IntegerField(choices=[(i, i) for i in range(1, 6)])  # Оценка от 1 до 5
    review = models.TextField(blank=True, null=True)  # Письменный отзыв
    image = models.ImageField(upload_to='reviews/', blank=True, null=True)  # Изображение отзыва

    def __str__(self):
        product_name = self.product.name if self.product else "Unknown"
        return f"{self.user.username} - Оценка: {self.value} - Продавец: {self.seller.username} - Товар: {product_name}"

@receiver(post_save, sender=Rating)
def update_user_quality_rating(sender, instance, created, **kwargs):
    if created:
        user = instance.user
        user_quality_rating = calculate_user_quality_rating(user)
        user.userprofile.quality_rating = user_quality_rating
        user.userprofile.save()

        product_avg_rating = Rating.objects.filter(product=instance.product).aggregate(Avg('value'))['value__avg']
        instance.product.rating = product_avg_rating
        instance.product.save()
def calculate_user_quality_rating(user):
    # Получаем все товары, продаваемые пользователем
    user_products = Product.objects.filter(seller=user)

    # Вычисляем средние оценки для всех товаров пользователя
    product_ratings = [product.ratings.aggregate(Avg('value'))['value__avg'] for product in user_products]

    # Исключаем None значения (если товар еще не был оценен)
    product_ratings = [rating for rating in product_ratings if rating is not None]

    # Вычисляем общую среднюю оценку качества пользователя
    if product_ratings:
        user_quality_rating = sum(product_ratings) / len(product_ratings)
        user_quality_rating = round(user_quality_rating, 2)  # Округляем до двух знаков после запятой
    else:
        user_quality_rating = Decimal('0.00')  # Если у пользователя нет оценок, устанавливаем нулевую оценку

    return user_quality_rating


# Часть пользователя
class UserProfile(models.Model):
    STATUS_CHOICES = (
        ('online', 'Online'),
        ('offline', 'Offline'),
    )

    user = models.OneToOneField(User, on_delete=models.CASCADE)
    avatar = models.ImageField(upload_to='avatars/', default='avatars/default.jpg')
    status = models.CharField(max_length=10, choices=STATUS_CHOICES, default='online')
    bio = models.TextField(blank=True, null=True)
    quality_rating = models.DecimalField(max_digits=3, decimal_places=2, default=0.00)
    first_name = models.CharField(max_length=50, blank=True, null=True)
    last_name = models.CharField(max_length=50, blank=True, null=True)
    patronymic = models.CharField(max_length=50, blank=True, null=True)
    last_activity = models.DateTimeField(default=timezone.now)

    def __str__(self):
        return self.user.username

@receiver(post_save, sender=Rating)
def update_user_quality_rating(sender, instance, created, **kwargs):
    if created:
        user = instance.user
        user_ratings = Rating.objects.filter(user=user)
        product_ratings = Rating.objects.filter(product=instance.product)

        # Обновляем рейтинг качества пользователя
        user_quality_rating = calculate_user_quality_rating(user)
        user.userprofile.quality_rating = user_quality_rating
        user.userprofile.save()

        # Обновляем средний рейтинг товара
        product_avg_rating = product_ratings.aggregate(Avg('value'))['value__avg']
        instance.product.rating = product_avg_rating
        instance.product.save()

@receiver(post_save, sender=User)
def create_user_profile(sender, instance, created, **kwargs):
    if created:
        UserProfile.objects.create(user=instance)

@receiver(post_save, sender=User)
def save_user_profile(sender, instance, **kwargs):
    instance.userprofile.save()

# @receiver(post_save, sender=UserProfile)
# def update_user_status(sender, instance, created, **kwargs):
#     if not created and not hasattr(instance, '_status_update_in_progress'):
#         instance._status_update_in_progress = True  # Устанавливаем флаг, чтобы избежать повторного выполнения
#         # Проверяем, была ли активность пользователя за последние 15 минут
#         threshold = timezone.now() - timezone.timedelta(minutes=1)
#         print('a')
#         print(threshold)
#         print(instance.last_activity)
#         if instance.last_activity > threshold:
#             # Если пользователь был неактивен, меняем его статус на "offline"
#             instance.status = 'online'
#         else:
#             # Иначе, пользователь активен, меняем его статус на "online"
#             instance.status = 'offline'
#         # Сохраняем изменения статуса пользователя
#         instance.save()
#         del instance._status_update_in_progress

class UserFinance(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    balance = models.DecimalField(max_digits=10, decimal_places=2, default=0.00)

    def __str__(self):
        return self.user.username + "'s finance"



# Часть чата
class Chat(models.Model):
    participants = models.ManyToManyField(User, related_name='chats')
    name = models.CharField(max_length=255, blank=True)  # Поле для названия чата

    def update_name(self):
        self.name = ', '.join(str(participant) for participant in self.participants.all())
        self.save()

    def add_participant(self, participant):
        self.participants.add(participant)
        self.update_name()

    def remove_participant(self, participant):
        self.participants.remove(participant)
        self.update_name()

    def __str__(self):
        if self.name:
            return self.name
        else:
            return ', '.join([str(participant) for participant in self.participants.all()])

    def last_message(self):
        return self.messages.order_by('-timestamp').first()


class Message(models.Model):
    chat = models.ForeignKey(Chat, on_delete=models.CASCADE, related_name='messages')
    sender = models.ForeignKey(User, on_delete=models.CASCADE)
    content = models.TextField()
    timestamp = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.content

class BlockedUser(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    chat = models.ForeignKey(Chat, on_delete=models.CASCADE)
    blocked_by = models.ForeignKey(User, related_name='blocked_by', on_delete=models.CASCADE)
    timestamp = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"User: {self.blocked_by} Blocked: {self.user}"

class UserComplaint(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    chat = models.ForeignKey(Chat, on_delete=models.CASCADE)
    complainant = models.ForeignKey(User, related_name='complainant', on_delete=models.CASCADE)
    reason = models.TextField()
    timestamp = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Chat: {self.chat}, User: {self.user} {self.reason}"


# Способ оплаты
class PaymentMethod(models.Model):
    name = models.CharField(max_length=100)
    description = models.TextField(blank=True)

    def __str__(self):
        return self.name

class DeliveryMethod(models.Model):
    name = models.CharField(max_length=100)
    description = models.TextField(max_length=1000)

    def __str__(self):
        return self.name

# Заказ
class Transaction(models.Model):
    buyer = models.ForeignKey(User, on_delete=models.CASCADE, related_name='purchased_transactions')
    seller = models.ForeignKey(User, on_delete=models.CASCADE, related_name='sold_transactions')
    product = models.ForeignKey(Product, on_delete=models.CASCADE)
    quantity = models.PositiveIntegerField(default=1)
    total_amount = models.DecimalField(max_digits=10, decimal_places=2)
    created_at = models.DateTimeField(auto_now_add=True)
    is_cancelled = models.BooleanField(default=False)

    def __str__(self):
        return f"Transaction #{self.id}"

    def cancel(self):
        # Если транзакция была отменена, ничего не делаем
        if self.is_cancelled:
            return

        # Вернуть средства покупателю
        self.buyer.userfinance.balance += self.total_amount
        self.buyer.userfinance.save()

        # Списать средства у продавца


        # Отметить транзакцию как отмененную
        self.is_cancelled = True
        self.save()


class ReservedOrder(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    first_name = models.CharField(max_length=50)
    last_name = models.CharField(max_length=50)
    patronymic = models.CharField(max_length=50)
    payment_method = models.ForeignKey(PaymentMethod, on_delete=models.CASCADE)
    delivery_method = models.ForeignKey(DeliveryMethod, on_delete=models.CASCADE)
    product = models.ForeignKey('Product', on_delete=models.CASCADE)
    quantity = models.PositiveIntegerField(default=1)
    total_amount = models.DecimalField(max_digits=10, decimal_places=2)
    city = models.CharField(max_length=100)
    address = models.CharField(max_length=200)
    serial_number = models.CharField(max_length=50, unique=True)
    # другие поля по усмотрению
    created_at = models.DateTimeField(default=timezone.now)
    paid = models.BooleanField(default=False)
    delivered = models.BooleanField(default=False)

    def __str__(self):
        return f"ReservedOrder #{self.id} - Paid: {self.paid} - Serial_number: {self.serial_number}"

class Order(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    first_name = models.CharField(max_length=50)
    last_name = models.CharField(max_length=50)
    patronymic = models.CharField(max_length=50)
    payment_method = models.ForeignKey(PaymentMethod, on_delete=models.CASCADE)
    delivery_method = models.ForeignKey(DeliveryMethod, on_delete=models.CASCADE)
    product = models.ForeignKey(Product, on_delete=models.CASCADE)  # Добавлено поле для товара
    quantity = models.PositiveIntegerField(default=1)
    total_amount = models.DecimalField(max_digits=10, decimal_places=2)
    city = models.CharField(max_length=100)
    address = models.CharField(max_length=200)
    serial_number = models.CharField(max_length=50, unique=True)
    transaction = models.ForeignKey(Transaction, on_delete=models.CASCADE, null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    paid = models.BooleanField(default=False)
    delivered = models.BooleanField(default=False)

    def __str__(self):
        return f"Order #{self.id} - Serial_number: {self.serial_number}"

    def cancel_order(self):
        """
        Метод для отмены заказа и возврата средств пользователю.
        """
        # Пометить заказ как отмененный
        self.delivered = False  # Предположим, что delivered отвечает за статус доставки
        self.save()

        # Вернуть средства пользователю
        if self.transaction:
            # Отметить транзакцию как отмененную или выполнить другие действия, связанные с возвратом средств
            self.transaction.cancel()  # Предполагается, что у Transaction есть метод cancel() для отмены транзакции


# Доставка



class PostOffice(models.Model):
    code = models.CharField(max_length=20)
    city = models.CharField(max_length=100)
    office_name = models.CharField(max_length=100)
    address = models.CharField(max_length=200)
    phone = models.CharField(max_length=50)
    email = models.EmailField()
    metro_stations = models.TextField()
    bus_stops = models.TextField()
    schedule = models.TextField()
    live_streaming = models.URLField(blank=True)
    fitting_room = models.BooleanField(default=False)
    cashless_payment = models.BooleanField(default=False)

    def __str__(self):
        return self.office_name