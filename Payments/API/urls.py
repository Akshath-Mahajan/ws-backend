from django.urls import path
from .views import OrderCRUD, UserOrders, OnlinePayment, RP_Success
# stripe_webhook
urlpatterns = [
    path('order/', OrderCRUD.as_view()),
    path('order/<int:pk>', OrderCRUD.as_view()),
    # path('refund/', RefundRequestCRUD.as_view()),
    # path('payment/', PaymentCRUD.as_view()),
    path('user-orders/', UserOrders.as_view()),
    # path('user-payments/', UserPayment.as_view()),
    # path('user-refunds/', UserRefunds.as_view()),
    path('checkout/', OnlinePayment.as_view()),
    path('rp-success/', RP_Success),
    # path('hook/', stripe_webhook),
]

