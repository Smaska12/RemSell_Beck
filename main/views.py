from django.shortcuts import render, redirect, get_object_or_404
from .models import Product, Category, Chat, Message, UserProfile, Rating, DeliveryMethod, PaymentMethod, UserFinance, PostOffice, ReservedOrder, Order, Transaction, BlockedUser, UserComplaint
from .forms import ProductForm, NotificationSettingsForm, SecuritySettingsForm, UpdateEmailForm, BioForm, CheckoutForm, AvatarForm
from django.db.models import Count, Q, Avg
from django.http import JsonResponse, HttpResponseRedirect
from django.urls import reverse
from .middleware import UserActivityMiddleware
from django.contrib.auth.decorators import login_required
from django.contrib.auth.forms import PasswordChangeForm, UserChangeForm
from django.contrib.auth import update_session_auth_hash, logout
from django.contrib.auth.models import User
from django.contrib import messages
from decimal import Decimal
from django.utils.html import linebreaks
import pandas as pd
from django.utils import timezone
import uuid, traceback, logging
from datetime import timedelta


categories = Category.objects.all()
logger = logging.getLogger(__name__)

def index(request):
    products = Product.objects.annotate(avg_rating=Avg('ratings__value'))
    search_query = request.GET.get('q')
    if search_query:
        # Filter products by name or description containing the search query
        products = products.filter(Q(name__icontains=search_query))
    return render(request, 'main/index.html', {'products': products, 'categories': categories, 'stars_range': range(1, 6)})

def chat(request):
        user = request.user
        finance = UserFinance.objects.get_or_create(user=user)[0]
        if user.is_authenticated and hasattr(user, 'userprofile'):
            user_avatar = user.userprofile.avatar.url
        user_chats = user.chats.all()  # Получаем все чаты, в которых участвует пользователь
        for chat in user_chats:
            if chat.participants.count() == 2:
                # Получаем другого участника чата
                other_participant = chat.participants.exclude(id=user.id).first()
                # Добавляем атрибут avatar к каждому чату
                chat.interlocutor_avatar = other_participant.userprofile.avatar.url if hasattr(other_participant,
                                                                                               'userprofile') else 'путь_к_изображению_по_умолчанию'
                chat.name = other_participant.username  # Устанавливаем имя пользователя как название чата
                chat.registration_date = other_participant.date_joined
        # Получаем все сообщения для всех чатов пользователя
        messages = Message.objects.filter(chat__in=user_chats)
        participants = chat.participants.all()
        interlocutor = participants.exclude(id=request.user.id).first()

        return render(request, 'main/chat.html', {'categories': categories, 'user_chats': user_chats, 'messages': messages, 'interlocutor': interlocutor, 'user_avatar': user_avatar, 'finance': finance})

def view_chat(request, chat_id):
    user = request.user
    chat_view = Chat.objects.get(pk=chat_id)
    user_profile = UserProfile.objects.get(user=request.user)
    finance = UserFinance.objects.get_or_create(user=user)[0]

    if user.is_authenticated and hasattr(user, 'userprofile'):
        user_avatar = user.userprofile.avatar.url

    user_is_blocked = False
    # Проверяем, заблокирован ли текущий пользователь в этом чате
    if BlockedUser.objects.filter(chat=chat_view, user=request.user).exists():
        user_is_blocked = True

    # Получаем всех участников чата
    participants = chat_view.participants.all()

    # Извлекаем собеседника, исключая текущего пользователя
    interlocutor = participants.exclude(id=request.user.id).first()
    messages = Message.objects.filter(chat=chat_view)

    current_user_is_blocker = BlockedUser.objects.filter(chat=chat_view, user=interlocutor, blocked_by=request.user).exists()

    # Получаем дату регистрации собеседника
    interlocutor_registration_date = interlocutor.date_joined.strftime('%Y-%m-%d')

    user_chats = user.chats.all()  # Получаем все чаты пользователя
    for other_chat in user_chats:  # Переименовываем переменную chat в other_chat
        if other_chat.participants.count() == 2:
            # Получаем другого участника чата
            other_participant = other_chat.participants.exclude(id=user.id).first()
            # Добавляем атрибут avatar к каждому чату
            other_chat.interlocutor_avatar = other_participant.userprofile.avatar.url if hasattr(other_participant,
                                                                                                 'userprofile') else 'путь_к_изображению_по_умолчанию'
            other_chat.name = other_participant.username  # Устанавливаем имя пользователя как название чата
            other_chat.registration_date = other_participant.date_joined

    return render(request, 'main/view_chat.html', {'chat': chat_view, 'messages': messages, 'interlocutor': interlocutor, 'interlocutor_registration_date': interlocutor_registration_date, 'categories': categories, 'user_chats': user_chats, 'user_avatar': user_avatar, 'finance': finance, 'user_profile': user_profile, 'user_is_blocked': user_is_blocked, 'current_user_is_blocker': current_user_is_blocker})

def log(request):
    user = request.user
    finance = UserFinance.objects.get_or_create(user=user)[0]
    products = Product.objects.exclude(seller=user).annotate(avg_rating=Avg('ratings__value'))

    search_query = request.GET.get('q')
    if search_query:
        # Filter products by name or description containing the search query
        products = products.filter(Q(name__icontains=search_query))

    if user.is_authenticated and hasattr(user, 'userprofile'):
        user_avatar = user.userprofile.avatar.url

    return render(request, 'main/log.html', {'products': products, 'categories': categories, 'user': user, 'user_avatar': user_avatar, 'finance': finance, 'stars_range': range(1, 6)})

def my_logout_view(request):
    logout(request)
    return redirect('entry')

def finance(request):
    user = request.user
    finance = UserFinance.objects.get_or_create(user=user)[0]
    orders = ReservedOrder.objects.filter(user=user)
    sales = Order.objects.filter(user=user)
    if user.is_authenticated and hasattr(user, 'userprofile'):
        user_avatar = user.userprofile.avatar.url

    context = {
        'orders': orders,
        'user_avatar': user_avatar,
        'finance': finance,
        'sales': sales,
    }
    return render(request, 'main/finance.html', context)

def sales_history(request):
    user = request.user
    finance = UserFinance.objects.get_or_create(user=user)[0]
    sales = Order.objects.filter(product__seller=user)
    if user.is_authenticated and hasattr(user, 'userprofile'):
        user_avatar = user.userprofile.avatar.url

    context = {
        'sales': sales,
        'user_avatar': user_avatar,
        'finance': finance
    }

    return render(request, 'main/sales_history.html', context)

def ship_order(request, order_id):
    try:
        order = Order.objects.get(id=order_id)

        # Check if the order has an associated transaction
        if order.transaction:
            order.delivered = True
            order.save()

            # Update the associated transaction status
            transaction = order.transaction
            transaction.delivered = True
            transaction.save()

            return JsonResponse({'message': 'Order shipped'})
        else:
            return JsonResponse({'message': 'Order does not have an associated transaction'}, status=400)
    except Exception as e:
        traceback.print_exc()
        return JsonResponse({'message': str(e)}, status=500)

def pay_order(request, order_id):
    try:
        reserved_order = ReservedOrder.objects.get(id=order_id)
        user = request.user
        finance = UserFinance.objects.get(user=user)

        if finance.balance >= reserved_order.total_amount:
            finance.balance -= reserved_order.total_amount
            finance.save()

            # Create the Order object
            order = Order.objects.create(
                user=user,
                first_name=reserved_order.first_name,
                last_name=reserved_order.last_name,
                patronymic=reserved_order.patronymic,
                payment_method=reserved_order.payment_method,
                delivery_method=reserved_order.delivery_method,
                product=reserved_order.product,
                quantity=reserved_order.quantity,
                total_amount=reserved_order.total_amount,
                city=reserved_order.city,
                address=reserved_order.address,
                serial_number=reserved_order.serial_number,
                created_at=reserved_order.created_at,
                paid=True,
                delivered=False
            )

            # Copy the delivery parameter from ReservedOrder to Order
            order.delivered = reserved_order.delivered
            order.save()

            # Optionally, you may delete the reserved order
            reserved_order.delete()

            # Create a transaction
            transaction = Transaction.objects.create(
                buyer=user,
                seller=reserved_order.product.seller,
                product=reserved_order.product,
                quantity=reserved_order.quantity,
                total_amount=reserved_order.total_amount
            )

            # Associate the transaction with the order
            order.transaction = transaction
            order.save()

            return redirect('product_detail_with_chat', product_id=order.product.id, order_id=order.id)
        else:
            return JsonResponse({'message': 'Insufficient balance'}, status=400)
    except Exception as e:
        traceback.print_exc()
        return JsonResponse({'message': str(e)}, status=500)

def confirm_payment(request, order_id):
    try:
        order = get_object_or_404(Order, pk=order_id, user=request.user)
        seller_finance = get_object_or_404(UserFinance, user=order.product.seller)

        if not order.delivered:
            order.delivered = True
            order.save()

            seller_finance.balance += order.total_amount
            seller_finance.save()

            return redirect('product_detail_with_chat', product_id=order.product.id, order_id=order.id)
        else:
            return JsonResponse({'message': 'Order is already delivered'}, status=400)
    except Exception as e:
        traceback.print_exc()
        return JsonResponse({'message': str(e)}, status=500)

def cancel_order(request, order_id):
    try:
        order = Order.objects.get(id=order_id)
        order.cancel_order()  # Вызываем метод отмены заказа
        return redirect('sales_history')
    except Order.DoesNotExist:
        return JsonResponse({'message': 'Order not found'}, status=404)
    except Exception as e:
        return JsonResponse({'message': str(e)}, status=500)

def add_product(request):
    user = request.user
    if user.is_authenticated and hasattr(user, 'userprofile'):
        user_avatar = user.userprofile.avatar.url

    finance = UserFinance.objects.get_or_create(user=user)[0]
    if request.method == 'POST':
        form = ProductForm(request.POST, request.FILES)
        if form.is_valid():
            product = form.save(commit=False)
            if request.user.is_authenticated:
                product.seller = request.user  # Устанавливаем текущего пользователя как продавца товара
            product.save()
            form.save_m2m()  # Сохранить многие-ко-многим отношения
            return redirect('log')
    else:
        form = ProductForm()
    return render(request, 'main/add_product.html', {'form': form, 'categories': categories, 'finance': finance, 'user_avatar': user_avatar})


def category_products(request, category_id):
    user = request.user
    finance = UserFinance.objects.get_or_create(user=user)[0]
    category = get_object_or_404(Category, pk=category_id)
    products = Product.objects.filter(categories=category)  # Использование связи "многие ко многим"
    categories = Category.objects.all()

    user_avatar = None
    if request.user.is_authenticated and hasattr(request.user, 'userprofile'):
        user_avatar = request.user.userprofile.avatar.url

    return render(request, 'main/category_products.html', {
        'category': category,
        'products': products,
        'categories': categories,
        'user': user,
        'stars_range': range(1, 6),
        'user_avatar': user_avatar,
        'finance': finance
    })


def send_message(request):
    if request.method == "POST":
        user = request.user
        chat_id = request.POST.get("chat_id")
        content = request.POST.get("content")
        chat = get_object_or_404(Chat, pk=chat_id)

        # Проверяем, заблокирован ли отправитель сообщения в чате
        blocked_user = BlockedUser.objects.filter(chat=chat, user=request.user).first()
        if blocked_user:
            # Если заблокирован, удаляем блокировку
            blocked_user.delete()

        try:
            chat = Chat.objects.get(pk=chat_id)
        except Chat.DoesNotExist:
            return JsonResponse({"success": False, "error": "Chat does not exist"})

        # Создаем новое сообщение и сохраняем его
        message = Message.objects.create(chat=chat, sender=user, content=content)

        # Возвращаем успешный ответ
        return JsonResponse({"success": True})
    else:

        return JsonResponse({"success": False, "error": "Invalid request method or not an AJAX request"})


def get_chat_messages(request):
    # Получаем chat_id из параметров запроса
    chat_id = request.GET.get('chat_id')

    # Получаем все сообщения чата с указанным chat_id
    chat_messages = Message.objects.filter(chat_id=chat_id)

    # Преобразуем сообщения чата в список словарей, содержащих данные о каждом сообщении
    messages_data = []
    for message in chat_messages:
        message_data = {
            'sender': message.sender.username,
            'content': message.content,
            'timestamp': message.timestamp.strftime('%Y-%m-%d %H:%M:%S'),  # Преобразуем дату и время в строку
            'chat_id': message.chat.id
        }
        messages_data.append(message_data)

    # Формируем данные для JSON-ответа
    data = {
        'messages': messages_data,
    }

    # Возвращаем JSON-ответ
    return JsonResponse(data)

def block_user(request):
    if request.method == 'POST':
        chat_id = request.POST.get('chat_id')
        user_id = request.POST.get('user_id')  # ID пользователя, которого нужно заблокировать

        chat = get_object_or_404(Chat, pk=chat_id)
        user_to_block = get_object_or_404(User, pk=user_id)

        # Проверяем, не заблокирован ли пользователь уже в этом чате
        if BlockedUser.objects.filter(chat=chat, user=user_to_block).exists():
            return JsonResponse({"success": False, "error": "User is already blocked in this chat"})

        # Создаем запись о блокировке пользователя в чате
        blocked_user = BlockedUser.objects.create(chat=chat, user=user_to_block, blocked_by=request.user)

        # Отправляем сообщение об обновлении
        message_content = f"{user_to_block.username} был заблокирован в этом чате."
        Message.objects.create(chat=chat, sender=request.user, content=message_content)

        return JsonResponse({"success": True})
    else:
        return JsonResponse({"success": False, "error": "Invalid request method"})

def unblock_user(request):
    if request.method == 'POST':
        chat_id = request.POST.get('chat_id')
        user_id = request.POST.get('user_id')

        chat = get_object_or_404(Chat, pk=chat_id)
        user_to_block = get_object_or_404(User, pk=user_id)

        logger.info(f"Received chat_id: {chat_id}, user_id: {user_id}")

        if not user_id or not chat_id:
            logger.error("Missing parameters")
            return JsonResponse({"success": False, "error": "Missing parameters"})

        try:
            blocked_user = get_object_or_404(BlockedUser, user_id=user_id, chat_id=chat_id)
            blocked_user.delete()

            message_content = f"{user_to_block.username} был разблокирован."
            Message.objects.create(chat=chat, sender=request.user, content=message_content)

            return JsonResponse({"success": True})
        except BlockedUser.DoesNotExist:
            logger.error(f"No BlockedUser matches the given query: user_id={user_id}, chat_id={chat_id}")
            return JsonResponse({"success": False, "error": "No BlockedUser matches the given query"})
    else:
        return JsonResponse({"success": False, "error": "Invalid request method"})

def report_user(request):
    if request.method == 'POST':
        chat_id = request.POST.get('chat_id')
        user_id = request.POST.get('user_id')  # ID пользователя, на которого жалуются
        reason = request.POST.get('reason')

        chat = get_object_or_404(Chat, pk=chat_id)
        user_to_report = get_object_or_404(User, pk=user_id)

        # Создаем запись о жалобе на пользователя
        complaint = UserComplaint.objects.create(chat=chat, user=user_to_report, complainant=request.user, reason=reason)

        # Возвращаем успешный ответ
        return JsonResponse({"success": True})
    else:
        return JsonResponse({"success": False, "error": "Invalid request method"})


def profile_user(request, username):
    user = request.user
    user_avatar = None  # Устанавливаем значение по умолчанию для user_avatar
    user_products = None
    finance = UserFinance.objects.get_or_create(user=user)[0]

    if request.user.is_authenticated and hasattr(request.user, 'userprofile'):
        user_avatar = request.user.userprofile.avatar.url

    user_profile = UserProfile.objects.get(user=request.user)

    # Фильтрация продуктов по рейтингу, если указан параметр rating в запросе
    rating_filter = request.GET.get('rating')
    if rating_filter:
        if rating_filter == '1-2':
            user_products = Product.objects.filter(
                seller=request.user
            ).annotate(avg_rating=Avg('ratings__value')).filter(avg_rating__gte=1, avg_rating__lt=2).order_by(
                '-created_at')[:5]
        elif rating_filter == '0':
            user_products = Product.objects.filter(
                seller=request.user
            ).annotate(avg_rating=Avg('ratings__value')).filter(
                Q(avg_rating__gte=0, avg_rating__lt=1) | Q(avg_rating__isnull=True)
            ).order_by('-created_at')[:5]
        elif rating_filter == '1':
            user_products = Product.objects.filter(
                seller=request.user
            ).annotate(avg_rating=Avg('ratings__value')).filter(avg_rating__gte=0.5, avg_rating__lt=1.5).order_by(
                '-created_at')[:5]
        elif rating_filter == '2':
            user_products = Product.objects.filter(
                seller=request.user
            ).annotate(avg_rating=Avg('ratings__value')).filter(avg_rating__gte=1.5, avg_rating__lt=2.5).order_by(
                '-created_at')[:5]
        elif rating_filter == '3':
            user_products = Product.objects.filter(
                seller=request.user
            ).annotate(avg_rating=Avg('ratings__value')).filter(avg_rating__gte=2.5, avg_rating__lt=3.5).order_by(
                '-created_at')[:5]
        elif rating_filter == '4':
            user_products = Product.objects.filter(
                seller=request.user
            ).annotate(avg_rating=Avg('ratings__value')).filter(avg_rating__gte=3.5, avg_rating__lt=4.5).order_by(
                '-created_at')[:5]
        elif rating_filter == '5':
            user_products = Product.objects.filter(
                seller=request.user
            ).annotate(avg_rating=Avg('ratings__value')).filter(avg_rating__gte=4.5, avg_rating__lte=5).order_by(
                '-created_at')[:5]
    else:
        user_products = Product.objects.filter(seller=request.user).annotate(avg_rating=Avg('ratings__value')).order_by(
            '-created_at')[:5]

    if request.method == 'POST':
        bio_form = BioForm(request.POST, instance=request.user.userprofile)
        if bio_form.is_valid():
            # Обновляем значение текста из формы
            bio_text = request.POST.get('bio')
            bio_text = bio_text.replace('\n', '<br>')
            bio_form.save()
            # Перенаправление на страницу профиля после сохранения
            return redirect(reverse('profile_user', args=[request.user.username]))
    else:
        bio_form = BioForm(instance=request.user.userprofile)

    current_time = timezone.now()
    fifteen_minutes_ago = current_time - timedelta(minutes=1)

    context = {
        'user_profile': user_profile,
        'user_products': user_products,
        'user_avatar': user_avatar,
        'stars_range': range(1, 6),
        'categories': categories,
        'bio_form': bio_form,
        'finance': finance,
        'current_time': current_time,
        'fifteen_minutes_ago': fifteen_minutes_ago,
    }

    return render(request, 'main/profile_user.html', context)

def view_other_profile(request, username):
    user = request.user
    user_avatar = None
    other_user = get_object_or_404(User, username=username)
    other_user_profile = other_user.userprofile
    other_user_avatar = other_user_profile.avatar.url
    finance = UserFinance.objects.get_or_create(user=user)[0]

    if request.user.is_authenticated and hasattr(request.user, 'userprofile'):
        user_avatar = request.user.userprofile.avatar.url

    # Получаем список продуктов другого пользователя
    other_user_products = Product.objects.filter(seller=other_user).annotate(avg_rating=Avg('ratings__value')).order_by(
        '-created_at')

    # Фильтрация продуктов другого пользователя по рейтингу, если указан параметр rating в запросе
    rating_filter = request.GET.get('rating')
    if rating_filter:
        if rating_filter == '1-2':
            other_user_products = other_user_products.filter(avg_rating__gte=1, avg_rating__lt=2)
        elif rating_filter == '0':
            other_user_products = other_user_products.filter(
                Q(avg_rating__gte=0, avg_rating__lt=1) | Q(avg_rating__isnull=True)
            )
        elif rating_filter == '1':
            other_user_products = other_user_products.filter(avg_rating__gte=0.5, avg_rating__lt=1.5)
        elif rating_filter == '2':
            other_user_products = other_user_products.filter(avg_rating__gte=1.5, avg_rating__lt=2.5)
        elif rating_filter == '3':
            other_user_products = other_user_products.filter(avg_rating__gte=2.5, avg_rating__lt=3.5)
        elif rating_filter == '4':
            other_user_products = other_user_products.filter(avg_rating__gte=3.5, avg_rating__lt=4.5)
        elif rating_filter == '5':
            other_user_products = other_user_products.filter(avg_rating__gte=4.5, avg_rating__lte=5)

    other_user_products = other_user_products[:5]  # Применяем срез после фильтрации

    bio_form = BioForm(instance=other_user_profile)

    current_time = timezone.now()
    fifteen_minutes_ago = current_time - timedelta(minutes=1)

    context = {
        'other_user_profile': other_user_profile,
        'user_avatar': user_avatar,
        'other_user': other_user,
        'other_user_products': other_user_products,
        'other_user_avatar': other_user_avatar,
        'stars_range': range(1, 6),
        'categories': categories,
        'bio_form': bio_form,
        'finance': finance,
        'current_time': current_time,
        'fifteen_minutes_ago': fifteen_minutes_ago,
    }
    # Передаем пользователя и его профиль в шаблон
    return render(request, 'main/view_other_profile.html', context)

def settings_user(request):
    user = request.user
    finance = UserFinance.objects.get_or_create(user=user)[0]
    user_avatar = None
    first_name = None
    last_name = None
    patronymic = None
    user_email = None

    if user.is_authenticated and hasattr(user, 'userprofile'):
        user_avatar = user.userprofile.avatar.url
        first_name = user.userprofile.first_name
        last_name = user.userprofile.last_name
        patronymic = user.userprofile.patronymic

    # Получение email пользователя
    if user.is_authenticated:
        user_email = user.email

    if request.method == 'POST':
        first_name = request.POST.get('first_name')
        last_name = request.POST.get('last_name')
        patronymic = request.POST.get('patronymic')

        user.userprofile.first_name = first_name
        user.userprofile.last_name = last_name
        user.userprofile.patronymic = patronymic
        user.userprofile.save()

    # Форма изменения пароля
    password_form = PasswordChangeForm(request.user)

    # Получаем экземпляр пользователя для передачи его в формы уведомлений и настроек безопасности
    user_instance = User.objects.get(pk=user.pk)

    # Формы уведомлений и настроек безопасности с предварительно заполненными данными пользователя
    notification_settings_form = NotificationSettingsForm(instance=user_instance)
    security_settings_form = SecuritySettingsForm(instance=user_instance)

    return render(request, 'main/settings_user.html', {
        'categories': categories,
        'user_avatar': user_avatar,
        'first_name': first_name,
        'last_name': last_name,
        'patronymic': patronymic,
        'password_form': password_form,
        'notification_settings_form': notification_settings_form,
        'security_settings_form': security_settings_form,
        'user_instance': user_instance,
        'user_email': user_email,
        'finance': finance,
    })

def product_detail(request, product_id):
    product = Product.objects.get(pk=product_id)

    if not product.available:  # Предположим, что у вас есть поле "available" в модели Product
        return redirect('product_not_available')  # Перенаправление на страницу "product_not_available"

    # Получаем продавца товара
    seller = product.seller

    user = request.user

    if user.is_authenticated and hasattr(user, 'userprofile'):
        user_avatar = user.userprofile.avatar.url

    finance = UserFinance.objects.get_or_create(user=user)[0]

    # Получаем все отзывы для текущего товара
    all_reviews = Rating.objects.filter(Q(product=product) | Q(product__isnull=True))

    # Получаем отзывы для всех товаров, проданных текущим продавцом
    seller_reviews = Rating.objects.filter(seller=seller)

    # Проверяем, есть ли уже чат между текущим пользователем и продавцом
    chat = Chat.objects.filter(participants=request.user).filter(participants=seller).first()

    # Если чат существует, используем его id, иначе создаем новый чат
    if chat:
        chat_id = chat.id
    else:
        chat = Chat.objects.create()  # Создаем новый чат
        chat.participants.add(request.user, seller)  # Добавляем участников
        chat_id = chat.id

    # Get messages for this chat
    messages = Message.objects.filter(chat=chat)

    user_is_blocked = False
    # Проверяем, заблокирован ли текущий пользователь в этом чате
    if BlockedUser.objects.filter(chat=chat, user=request.user).exists():
        user_is_blocked = True

    # Check if the current user has blocked the seller
    current_user_is_blocker = BlockedUser.objects.filter(chat=chat, user=seller, blocked_by=request.user).exists()

    # Вычисляем среднюю оценку продукта
    avg_rating = Rating.objects.filter(product=product).aggregate(Avg('value'))['value__avg']

    # Получаем список всех способов оплаты
    payment_methods = [
        {
            'name': method.name,
            'description': method.description,
        }
        for method in PaymentMethod.objects.all()
    ]

    # Получаем список всех способов доставки
    delivery_methods = [
        {
            'name': method.name,
            'description': method.description,
        }
        for method in DeliveryMethod.objects.all()
    ]

    context = {
        'product': product,
        'categories': categories,
        'product_categories': product.categories.all(),
        'stars_range': range(1, 6),
        'avg_rating': avg_rating,
        'user_avatar': user_avatar,
        'reviews_all': all_reviews,
        'reviews': seller_reviews,
        'seller': seller,
        'finance': finance,
        'user_is_blocked': user_is_blocked,
        'current_user_is_blocker': current_user_is_blocker,
    }

    context_chat = {
        'product': product,
        'categories': categories,
        'product_categories': product.categories.all(),
        'stars_range': range(1, 6),
        'avg_rating': avg_rating,
        'user_avatar': user_avatar,
        'reviews_all': all_reviews,
        'reviews': seller_reviews,
        'seller': seller,
        'chat_id': chat_id,
        'chat': chat,
        'messages': messages,
        'payment_methods': payment_methods,
        'delivery_methods': delivery_methods,
        'finance': finance,
        'user_is_blocked': user_is_blocked,
        'current_user_is_blocker': current_user_is_blocker,
    }

    if user == seller:
        # Если текущий пользователь является продавцом товара, используйте шаблон без чата
        return render(request, 'main/product_detail_no_chat.html', context)
    else:
        if 'review-type' in request.GET:
            review_type = request.GET['review-type']
            if review_type == 'product':
                context_chat['reviews'] = all_reviews.filter(product=product)
            elif review_type == 'seller':
                context_chat['reviews'] = seller_reviews

        if 'rating' in request.GET:
            rating = request.GET['rating']
            if rating.isdigit() and 1 <= int(rating) <= 5:
                context_chat['reviews'] = context_chat['reviews'].filter(value=rating)
        return render(request, 'main/product_detail.html', context_chat)

def product_detail_with_chat(request, product_id, order_id):
    product = Product.objects.get(pk=product_id)

    # Получаем продавца товара
    seller = product.seller

    user = request.user

    sales = Order.objects.filter(product__seller=user)

    if user.is_authenticated and hasattr(user, 'userprofile'):
        user_avatar = user.userprofile.avatar.url

    finance = UserFinance.objects.get_or_create(user=user)[0]

    # Получаем все отзывы для текущего товара
    all_reviews = Rating.objects.filter(Q(product=product) | Q(product__isnull=True))

    # Получаем отзывы для всех товаров, проданных текущим продавцом
    seller_reviews = Rating.objects.filter(seller=seller)

    # Проверяем, есть ли уже чат между текущим пользователем и продавцом
    product_chat = Chat.objects.filter(participants=request.user).filter(participants=seller).first()

    current_user_is_blocker = BlockedUser.objects.filter(chat=product_chat, user=seller, blocked_by=request.user).exists()

    # Если чат существует, используем его id, иначе создаем новый чат
    if product_chat:
        chat_id = product_chat.id
    else:
        product_chat = Chat.objects.create()  # Создаем новый чат
        product_chat.participants.add(request.user, seller)  # Добавляем участников
        chat_id = product_chat.id

    # Get messages for this chat
    messages = Message.objects.filter(chat=product_chat)

    # Вычисляем среднюю оценку продукта
    avg_rating = Rating.objects.filter(product=product).aggregate(Avg('value'))['value__avg']

    # Получаем список всех способов оплаты
    payment_methods = [
        {
            'name': method.name,
            'description': method.description,
        }
        for method in PaymentMethod.objects.all()
    ]

    # Получаем список всех способов доставки
    delivery_methods = [
        {
            'name': method.name,
            'description': method.description,
        }
        for method in DeliveryMethod.objects.all()
    ]

    reserved_order = ReservedOrder.objects.filter(product=product, user=user, id=order_id).first()
    order = Order.objects.filter(product=product, user=user, id=order_id).first()


    user_is_blocked = False
    # Проверяем, заблокирован ли текущий пользователь в этом чате
    if BlockedUser.objects.filter(chat=product_chat, user=request.user).exists():
        user_is_blocked = True

    context = {
        'product': product,
        'reserved_order': reserved_order,
        'order': order,
        'categories': categories,
        'product_categories': product.categories.all(),
        'stars_range': range(1, 6),
        'avg_rating': avg_rating,
        'user_avatar': user_avatar,
        'reviews_all': all_reviews,
        'reviews': seller_reviews,
        'seller': seller,
        'chat_id': chat_id,
        'chat': product_chat,
        'messages': messages,
        'finance': finance,
        'sales': sales,
        'user_is_blocked': user_is_blocked,
        'current_user_is_blocker': current_user_is_blocker,
    }

    context_chat = {
        'product': product,
        'reserved_order': reserved_order,
        'order': order,
        'categories': categories,
        'product_categories': product.categories.all(),
        'stars_range': range(1, 6),
        'avg_rating': avg_rating,
        'user_avatar': user_avatar,
        'reviews_all': all_reviews,
        'reviews': seller_reviews,
        'seller': seller,
        'chat_id': chat_id,
        'chat': product_chat,
        'messages': messages,
        'payment_methods': payment_methods,
        'delivery_methods': delivery_methods,
        'finance': finance,
        'sales': sales,
        'user_is_blocked': user_is_blocked,
        'current_user_is_blocker': current_user_is_blocker,
    }

    if user == seller:
        # Если текущий пользователь является продавцом товара, используйте шаблон без чата
        return render(request, 'main/product_detail_with_chat.html', context)
    else:
        if 'review-type' in request.GET:
            review_type = request.GET['review-type']
            if review_type == 'product':
                context_chat['reviews'] = all_reviews.filter(product=product)
            elif review_type == 'seller':
                context_chat['reviews'] = seller_reviews

        if 'rating' in request.GET:
            rating = request.GET['rating']
            if rating.isdigit() and 1 <= int(rating) <= 5:
                context_chat['reviews'] = context_chat['reviews'].filter(value=rating)

        # Проверяем, написал ли пользователь отзыв для данного товара
        has_review = Rating.objects.filter(product=product, user=user).exists()

        # Добавляем переменную has_review в контекст
        context_chat['has_review'] = has_review

        return render(request, 'main/product_detail_with_chat.html', context_chat)


def leave_review(request):
    if request.method == 'POST':
        rating_value = request.POST.get('rating')  # Получение значения рейтинга из POST-запроса
        review_content = request.POST.get('review_content')  # Получение содержимого отзыва из POST-запроса

        # Получение продукта, для которого оставляется отзыв
        product_id = request.POST.get('product_id')
        product = Product.objects.get(id=product_id)

        # Получение продавца товара
        seller = product.seller

        # Создание экземпляра модели Rating с установленным seller_id
        Rating.objects.create(
            user=request.user,
            seller=seller,  # Установка продавца товара
            product=product,
            value=rating_value,
            review=review_content
        )

        return redirect('product_detail_with_chat', order_id=product_id)
    else:
        return redirect('home')  # Перенаправление на домашнюю страницу, если запрос не является POST-запросом


def update_username(request):
    if request.method == 'POST':
        new_username = request.POST.get('new_username')
        user = request.user
        user.username = new_username
        user.save()
        return JsonResponse({'success': True})
    else:
        return JsonResponse({'success': False, 'message': 'Invalid request method'})

def update_password(request):
    if request.method == 'POST':
        form = PasswordChangeForm(user=request.user, data=request.POST)
        if form.is_valid():
            form.save()
            return JsonResponse({'success': True, 'redirect_url': '/account/entry'})
        else:
            return JsonResponse({'success': False, 'errors': form.errors}, status=400)
    else:
        return JsonResponse({'success': False, 'message': 'Invalid request method'}, status=405)

def update_email(request):
    if request.method == 'POST':
        form = UpdateEmailForm(request.POST)
        if form.is_valid():
            new_email = form.cleaned_data['email']
            # Ваш код сохранения нового email
            user = request.user
            user.email = new_email
            user.save()
            return JsonResponse({'success': True})
        else:
            errors = form.errors.as_json()
            return JsonResponse({'success': False, 'errors': errors}, status=400)
    else:
        return JsonResponse({'success': False, 'message': 'Invalid request method'}, status=405)

def update_security(request):
    if request.method == 'POST':
        form = PasswordChangeForm(user=request.user, data=request.POST)
        if form.is_valid():
            user = form.save()
            update_session_auth_hash(request, user)  # Important to keep the user logged in
            messages.success(request, 'Your password was successfully updated!')
            return JsonResponse({'success': True})
        else:
            return JsonResponse({'success': False, 'errors': form.errors}, status=400)
    else:
        return JsonResponse({'success': False, 'message': 'Неверный метод запроса'}, status=405)

def update_avatar(request):
    if request.method == 'POST':
        form = AvatarForm(request.POST, request.FILES, instance=request.user.userprofile)
        if form.is_valid():
            form.save()
            return redirect('settings_user')  # Перенаправляем пользователя на его профиль
    else:
        form = AvatarForm(instance=request.user.userprofile)
    return render(request, 'settings_user.html', {'form': form})

def product_not_available(request):
    user = request.user

    if user.is_authenticated and hasattr(user, 'userprofile'):
        user_avatar = user.userprofile.avatar.url
    finance = UserFinance.objects.get_or_create(user=user)[0]
    return render(request, 'main/product_not_available.html', {'user': user, 'finance': finance, 'user_avatar': user_avatar})

def update_user_status(request):
    if request.user.is_authenticated:
        middleware = UserActivityMiddleware(get_response=None)
        user_profile = request.user.userprofile

        # Обновляем статус пользователя в зависимости от его активности
        if middleware.user_is_active(user_profile.last_activity):
            user_profile.status = 'online'
        else:
            user_profile.status = 'offline'

        user_profile.save()

        return JsonResponse({'status': user_profile.status})
    else:
        return JsonResponse({'status': 'anonymous'})

def order_checkout(request, product_id):
    product = Product.objects.get(pk=product_id)
    user = request.user
    user_avatar = None
    finance = UserFinance.objects.get_or_create(user=user)[0]

    # Получение данных пользователя
    if user.is_authenticated and hasattr(user, 'userprofile'):
        user_avatar = user.userprofile.avatar.url
        initial_data = {
            'first_name': user.userprofile.first_name,
            'last_name': user.userprofile.last_name,
            'patronymic': user.userprofile.patronymic if hasattr(user.userprofile, 'patronymic') else None,
            'email': user.email,
            # остальные данные при необходимости
        }
        form = CheckoutForm(initial=initial_data)
    else:
        form = CheckoutForm()

    cities = PostOffice.objects.values_list('city', flat=True).distinct()
    addresses = PostOffice.objects.values_list('address', flat=True)

    if request.method == 'POST':
        form = CheckoutForm(request.POST)
        if form.is_valid():
            quantity = form.cleaned_data['quantity']
            first_name = form.cleaned_data['first_name']
            last_name = form.cleaned_data['last_name']
            patronymic = form.cleaned_data['patronymic']
            if quantity <= product.quantity:
                city = request.POST.get('city')
                address = request.POST.get('address')
                delivery_method = form.cleaned_data['delivery_method']  # Получаем способ доставки из формы
                serial_number = str(uuid.uuid4())[:8]  # Генерируем серийный номер
                # Создание заказа
                total_price = product.price * quantity
                reserved_order = ReservedOrder.objects.create(
                    user=request.user,
                    first_name=first_name,
                    last_name=last_name,
                    patronymic=patronymic,
                    payment_method=form.cleaned_data['payment_method'],
                    product=product,
                    total_amount=total_price,
                    quantity=quantity,
                    city=city,
                    address=address,
                    serial_number=serial_number,
                    created_at=timezone.now(),
                    paid=False,
                    delivered=False,
                    delivery_method=delivery_method
                )
                reserved_order.save()

                # Обновление количества товара
                product.quantity -= quantity
                product.save()

                # Перенаправление на страницу подтверждения заказа
                return redirect('order_confirmation', product_id=product_id, reserved_order_id=reserved_order.id)
            else:
                form.add_error('quantity', 'Указанное количество превышает доступное количество товара.')
    else:
        pass

    context = {
        'user_avatar': user_avatar,
        'product': product,
        'form': form,
        'finance': finance,
        'cities': cities,
        'addresses': addresses
    }
    return render(request, 'main/order_checkout.html', context)


def order_confirmation(request, product_id, reserved_order_id):
    user = request.user
    if user.is_authenticated and hasattr(user, 'userprofile'):
        user_avatar = user.userprofile.avatar.url
    finance = UserFinance.objects.get_or_create(user=user)[0]
    # Получаем экземпляр модели ReservedOrder по его идентификатору
    reserved_order = ReservedOrder.objects.get(pk=reserved_order_id)

    # Здесь можно отобразить страницу подтверждения заказа с информацией о заказе
    context = {
        'user': user,
        'user_avatar': user_avatar,
        'finance': finance,
        'reserved_order': reserved_order,
    }
    return render(request, 'main/order_confirmation.html', context)

def autocomplete_address(request):
    if request.method == 'GET':
        city = request.GET.get('city', '')
        addresses = list(PostOffice.objects.filter(city=city).values_list('address', flat=True))
        return JsonResponse({'addresses': addresses})
    else:
        return JsonResponse({'error': 'Invalid request'})


def search_products(request):
    if 'q' in request.GET:
        query = request.GET['q']
        # Выполнить поиск товаров по названию или описанию
        results = Product.objects.filter(name__icontains=query) | Product.objects.filter(description__icontains=query)
        # Преобразовать результаты в формат JSON
        serialized_results = [{'name': product.name, 'description': product.description} for product in results]
        return JsonResponse(serialized_results, safe=False)
    else:
        return JsonResponse({'error': 'Invalid request'}, status=400)
