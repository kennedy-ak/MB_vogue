from django.urls import path
from . import views

app_name = 'payments'

urlpatterns = [
    path('initialize/<int:order_id>/', views.initialize_payment, name='initialize_payment'),
    path('verify/', views.verify_payment, name='verify_payment'),
    path('callback/', views.payment_callback, name='payment_callback'),
]
