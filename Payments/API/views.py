from django.http import HttpResponse, JsonResponse, Http404
from rest_framework.views import APIView
from rest_framework.permissions import AllowAny
from rest_framework.response import Response
from rest_framework import status
from .serializers import OrderItemSerializer, OrderSerializer, PaymentSerializer, RefundSerializer
from ..models import Order, OrderItem, Payment, RefundRequest
from Accounts.models import CartAndProduct, Address, Cart
from Products.models import Product
from django.contrib.auth import authenticate
import datetime


class UserOrders(APIView):
    def get(self, request, format=None):
        orders = Order.objects.filter(user=request.user)
        O_serializer = OrderSerializer(orders, many=True)
        return Response(O_serializer.data, status.HTTP_200_OK)
class OrderCRUD(APIView):
    def get(self, request, format=None):
        '''
            Get detailed view of a particular order
        '''
        pk = request.data['pk']
        order = Order.objects.get(id=pk, user=request.user)
        order_items = OrderItem.objects.filter(order=order)
        O_serializer = OrderSerializer(order)
        OI_serializer = OrderItemSerializer(order_items, many=True)
        data = {'order': O_serializer.data, 'order_items': OI_serializer.data}
        return Response(data, status=status.HTTP_200_OK)
    def post(self, request,format=None):
        '''
            Place new order
        '''
        address_id = request.data['address_id']
        address = Address.objects.get(pk=address_id, user=request.user)
        order = Order(user=request.user, address=address, payment_method=request.data['payment_method'])
        order.save()
        if request.data['method'] == 'buy_now':
            #request.data will contain product_id, size and quantity
            product = Product.objects.get(pk=request.data['product_id'])
            fp = (100-product.discount) * product.price/100
            OrderItem(product=product, order=order, name=product.name, 
                                    discount = product.discount, 
                                    initial_price = product.price, 
                                    final_price = fp, 
                                    quantity = request.data['quantity']).save()
        else:
            #request.user's cart
            cart = Cart.objects.get(user=request.user)
            cps = CartAndProduct.objects.filter(cart = cart)
            if cps.exists():
                for item in cps:
                    fp = (100-item.product.discount) * item.product.price/100
                    OrderItem(product=item.product, order=order, 
                    name=item.product.name, initial_price=item.product.price, 
                    discount=item.product.discount, final_price=fp, quantity=item.quantity).save()
            cps.delete()
        order_items = OrderItem.objects.filter(order=order)
        OI_serial = OrderItemSerializer(order_items, many=True)
        O_serial = OrderSerializer(order)
        data = {'order': O_serial.data, 'order_items': OI_serial.data}
        return Response(data, status=status.HTTP_200_OK)  
    def delete(self, request, format=None):
        pk = request.data['pk']
        order = Order.objects.get(pk=pk, user=request.user)
        threshold = datetime.date.today() - datetime.timedelta(days=1)
        if order.created_at.date() > threshold:
            #Allow cancellation
            order.delete()
            #Give back money if online payment
            return Response({'status': 1}, status=status.HTTP_200_OK)
        else:
            #Disallow cancellation
            return Response({'status': 0}, status=status.HTTP_200_OK)

class UserPayment(APIView):
    def get(self, request, format=None):
        payments = Payment.objects.filter(order__user=request.user)
        P_serializer = PaymentSerializer(payments, many=True)
        return Response(P_serializer.data, status.HTTP_200_OK)
class PaymentCRUD(APIView):
    def get(self, request, format=None):
        pk = request.data['pk']
        payment = Payment.objects.get(pk=pk, order__user=request.user)
        order = payment.order
        order_items = OrderItem.objects.filter(order=order)
        O_serializer = OrderSerializer(order)
        OI_serializer = OrderItemSerializer(order_items, many=True)
        P_serializer = PaymentSerializer(payment)
        data = {'order': O_serializer.data, 'order_items': OI_serializer.data, 'payment':P_serializer.data}
        return Response(data, status.HTTP_200_OK)
    def post(self, request, format=None):
        #Create a payment
        order = Order.objects.get(pk = request.data['order_id'], user=request.user)
        if order.payment_method == 1:
        # Dont send post request to API unless 
        # payment_method = 1, instead create payment obj manually
            p = Payment(order=order, amount=order.total, amt_paid = order.total, change=0)
            p.save()
            #Take money here
            serializer = PaymentSerializer(p)
            return Response(serializer.data, status.HTTP_200_OK)
class UserRefunds(APIView):
    pass
class RefundRequestCRUD(APIView):
    def get(self, request, format=None):
        pk = request.data['pk']
        refund = RefundRequest.objects.get(pk=pk, order_item__order__user = request.user)
        order_item = refund.order_item
        R_serializer = RefundSerializer(refund)
        OI_serializer = OrderItemSerializer(order_item)
        data = {'order_item': OI_serializer.data, 'refund':R_serializer.data}
        return Response(data, status.HTTP_200_OK)
    def post(self, request, format=None):
        # if OI has quantity > 1, then to 
        # refund n number send quantity with req
        # if quantity is not send with request
        # refund all
        OI_id = request.data['order_item_id']
        OI = OrderItem.objects.get(pk=OI_id)
        quantity = request.data.get('quantity', OI.quantity)
        RefundRequest(order_item=OI, quantity=quantity, amount=OI.final_price * quantity).save()
        return Response({'status': 'Request Created'}, status.HTTP_200_OK)
    def delete(self, request, format=None):
        pk = request.data['pk']
        refundReq = RefundRequest.objects.get(pk=pk, order_item__order__user=request.user)
        if not refundReq.granted:
            refundReq.delete()
            return Response({'status': 1}, status=status.HTTP_200_OK)
        else:
            return Response({'status': 0}, status=status.HTTP_200_OK)