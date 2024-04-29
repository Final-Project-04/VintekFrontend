from django.urls import path
from .views import CheckoutView, PaymentView, OrderConfirmationView,MyOrdersView,DeleteOrderView

app_name = 'order_and_payment'



urlpatterns = [
    
    path('checkout/', CheckoutView.as_view(), name='checkout'),
    path('payment/', PaymentView.as_view(), name='payment'),
    path('order_confirmation/<int:order_id>/', OrderConfirmationView.as_view(), name='order_confirmation'),
    path('payment/<int:order_id>/', PaymentView.as_view(), name='payment_with_order'),
    path('my_orders/', MyOrdersView.as_view(), name='my_orders'),
    path('delete_order/<int:order_id>/', DeleteOrderView.as_view(), name='delete_order'),

    
    ]