from django.contrib import admin
from .models import Product, Message, Category, UserProfile, Chat, Rating, Order, PaymentMethod, ReservedOrder
from .models import DeliveryMethod, UserFinance, PostOffice, Transaction
from .models import BlockedUser, UserComplaint

admin.site.register(Product)
admin.site.register(Category)
admin.site.register(UserProfile)
admin.site.register(Chat)
admin.site.register(Message)
admin.site.register(Rating)
admin.site.register(Order)
admin.site.register(ReservedOrder)
admin.site.register(PaymentMethod)
admin.site.register(DeliveryMethod)
admin.site.register(UserFinance)
admin.site.register(PostOffice)
admin.site.register(Transaction)
admin.site.register(BlockedUser)
admin.site.register(UserComplaint)