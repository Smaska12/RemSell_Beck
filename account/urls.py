from django.urls import path
from . import views

urlpatterns = [
    path('registration', views.reg, name='reg'),
    path('entry', views.entry, name='entry')
]
