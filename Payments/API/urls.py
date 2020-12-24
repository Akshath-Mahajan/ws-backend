from django.urls import path
from .views import OrderCRUD, RefundRequestCRUD, PaymentCRUD, UserOrders, UserPayment, UserRefunds
urlpatterns = [
    path('order/', OrderCRUD.as_view()),
    path('refund/', RefundRequestCRUD.as_view()),
    path('payment/', PaymentCRUD.as_view()),
    path('user-orders/', UserOrders.as_view()),
    path('user-payments/', UserPayment.as_view()),
    path('user-refunds/', UserRefunds.as_view()),
]

