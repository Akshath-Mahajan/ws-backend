from django.http import HttpResponse, JsonResponse, Http404
from rest_framework.views import APIView
from rest_framework.permissions import AllowAny
from rest_framework.response import Response
from rest_framework import status
from .serializers import OrderItemSerializer, OrderSerializer, PaymentSerializer, RefundSerializer
from ..models import Order, OrderItem, Payment, RefundRequest
from Accounts.models import CartAndProduct, Address
from Products.models import Product
from django.contrib.auth import authenticate
import datetime


class UserOrders(APIView):
    def get(self, request, format=None):
        # Get all orders of user
        pass
class OrderCRUD(APIView):
    def get(self, request, pk, format=None):
        '''
            Get detailed view of a particular order
        '''
        order = Order.objects.get(id=pk, user=request.user)
        order_items = OrderItem.objects.filter(order=order)
        O_serializer = OrderSerializer(order)
        OI_serializer = OrderItemSerializer(order_items)
        data = {'order': O_serializer.data, 'order_items': OI_serializer.data}
        return Response(data, status=status.HTTP_200_OK)
    def post(self, request,format=None):
        '''
            Place new order
        '''
        address_id = request.data['address_id']
        address = Address.objects.get(pk=address_id, user=request.user)
        order = Order(user=request.user, address=address, payment_method=request.data['payment_method']).save()
        if request.data['method'] == 'buy_now':
            #request.data will contain product_id, size and quantity
            product = Product.objects.get(pk=request.data['product_id'])
            fp = (100-product.discount) * product.initial_price/100
            OrderItem(product=product, order=order, name=product.name, 
                                    discount = product.discount, 
                                    initial_price = product.price, 
                                    final_price = fp, 
                                    quantity = request.data['quantity']).save()
        else:
            #request.data will contain cps = CartAndProduct items array
            pks = request.data['cps']
            cps = CartAndProduct.objects.filter(pk__in = pks)
            if cps.exists():
                for item in cps:
                    fp = (100-item.discount) * item.initial_price/100
                    
                    OrderItem(product=item.product, order=order, 
                    name=item.name, initial_price=item.price, 
                    discount=item.discount, final_price=fp, quantity=item.quantity).save()
            cps.delete()
        order_items = OrderItem.objects.filter(order=order)
        OI_serial = OrderItemSerializer(order_items, many=True)
        O_serial = OrderSerializer(order)
        data = {'order': O_serial.data, 'order_items': OI_serial.data}
        return Response(data, status=status.HTTP_200_OK)  
    def delete(self, request, pk, format=None):
        order = Order.objects.get(pk=pk, user=request.user)
        threshold = datetime.date.today() - datetime.timedelta(days=1)
        if order.created_at > threshold:
            #Allow cancellation
            order.delete()
            #Give back money
            return Response({'status': 1}, status=status.HTTP_200_OK)
        else:
            #Disallow cancellation
            return Response({'status': 0}, status=status.HTTP_200_OK)

class UserPayment(APIView):
    pass
class PaymentCRUD(APIView):
    def get(self, request, pk, format=None):
        payment = Payment.objects.get(pk=pk)
        order = payment.order
        order_items = OrderItem.objects.filter(order=order)
        O_serializer = OrderSerializer(order)
        OI_serializer = OrderItemSerializer(order_items)
        P_serializer = PaymentSerializer(payment)
        data = {'order': O_serializer.data, 'order_items': OI_serializer.data, 'payment':P_serializer.data}
        return Response(data, status.HTTP_200_OK)
    def post(self, request, format=None):
        #Create a payment
        order = Order.objects.get(pk = request.data['order_id'])
        if order.payment_method == 1:
        # Dont send post request to API unless 
        # payment_method = 1, instead create payment obj manually
            p = Payment(order=order, amount=order.total, amt_paid = order.total, change=0).save()
            #Take money here
            serializer = PaymentSerializer(p)
            return Response(serializer.data, status.HTTP_200_OK)
class UserRefunds(APIView):
    pass
class RefundRequestCRUD(APIView):
    def get(self, request, pk, format=None):
        refund = RefundRequest.objects.get(pk=pk)
        order_item = refund.order_item
        R_serializer = RefundSerializer(refund)
        OI_serializer = OrderItemSerializer(order_item)
        data = {'order_item': OI_serializer.data, 'refund':R_serializer.data}
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
    def delete(self, request, pk, format=None):
        refundReq = RefundRequest.objects.get(pk=pk)
        if not refundReq.granted:
            refundReq.delete()
            return Response({'status': 1}, status=status.HTTP_200_OK)
        else:
            return Response({'status': 0}, status=status.HTTP_200_OK)