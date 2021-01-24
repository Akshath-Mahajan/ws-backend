from django.http import HttpResponse, JsonResponse, Http404
from rest_framework.views import APIView
from rest_framework.permissions import AllowAny
from rest_framework.response import Response
from rest_framework.decorators import api_view
from rest_framework import status
from .serializers import OrderItemSerializer, OrderSerializer
from ..models import Order, OrderItem, RP_Order
from Accounts.models import CartAndProduct, Address, Cart
from Products.models import Product
from django.contrib.auth import authenticate
import datetime
from django.conf import settings
from Accounts.models import User
import razorpay
import json
from django.http import HttpResponse
from django.views.decorators.csrf import csrf_exempt

@api_view(['POST'])
@csrf_exempt
def RP_Success(request):
    if request.method == "POST":
        a = request.data
        data = {}
        for key, val in a.items():
            if key == 'razorpay_order_id':
                data['razorpay_order_id'] = val
                order_id = val
            elif key == 'razorpay_payment_id':
                data['razorpay_payment_id'] = val
            elif key == 'razorpay_signature':
                data['razorpay_signature'] = val
        order = RP_Order.objects.filter(rp_order_id = order_id).first().order
        client = razorpay.Client(auth=(settings.RAZORPAY_PUBLIC_KEY, settings.RAZORPAY_SECRET_KEY))
        check = client.utility.verify_payment_signature(data)
        if check:   #If check is not none then it's error.
            return Response({'Error': 'Payment unsuccessful'}, status=status.HTTP_400_BAD_REQUEST)
        order.paid = True
        order.save()
        return Response({'Success': "Payment complete"}, status=status.HTTP_200_OK)
class UserOrders(APIView):
    def get(self, request, format=None):
        orders = Order.objects.filter(user=request.user).exclude(online_payment=True, paid=False)
        O_serializer = OrderSerializer(orders, many=True)
        return Response(O_serializer.data, status.HTTP_200_OK)


class OnlinePayment(APIView):
    def post(self, request):
        address = Address.objects.get(pk=request.data['address_id'], user=request.user)
        client = razorpay.Client(auth=(settings.RAZORPAY_PUBLIC_KEY, settings.RAZORPAY_SECRET_KEY))
        if request.data.get('buy_now', None):
            product = Product.objects.get(pk=request.data['product_id'])
            payment = client.order.create({
                'amount': (100-product.discount) * product.price * request.data['quantity'], #In paise
                'currency': 'INR', 'payment_capture': '1'
                })
            o = Order(user=request.user, 
            address=address.details+'\n'+address.locality+'\n'+address.landmark+'\n'+address.city+ '\n'+address.pincode, 
            online_payment=True, paid=False)
            o.save()
            OrderItem(order=o, name=product.name, 
                                    discount = product.discount, 
                                    initial_price = product.price, 
                                    final_price = (100-product.discount) * product.price * 0.01, 
                                    quantity = request.data['quantity'],
                                    size=request.data['size']).save()
            rp_o = RP_Order(order = o, rp_order_id=payment['id'])
            rp_o.save()
            return Response({'rzpay':payment}, status=status.HTTP_200_OK)
        else:
            cart = Cart.objects.get(user=request.user)
            cps = CartAndProduct.objects.filter(cart=cart)
            amt = 0 #In paise
            o = Order(
                user=request.user,
                address=address.details+'\n'+address.locality+'\n'+address.landmark+'\n'+address.city+ '\n'+address.pincode, 
                online_payment=True, paid=False
            )
            o.save()
            for cp in cps:
                OrderItem(
                    order = o, name=cp.product.name, discount=cp.product.discount, 
                    initial_price = cp.product.price, final_price=(100-cp.product.discount) * cp.product.price * 0.01,
                    quantity = cp.quantity,
                    size=cp.size).save()
                amt+= (100 - cp.product.discount) * cp.product.price * cp.quantity
            payment = client.order.create({
                'amount': amt, #In paise
                'currency': 'INR', 'payment_capture': '1'
            })
            rp_o = RP_Order(order = o, rp_order_id=payment['id'])
            rp_o.save()
            return Response({'rzpay':payment}, status=status.HTTP_200_OK)

class OrderCRUD(APIView):
    def get(self, request, pk, format=None):
        '''
            Get detailed view of a particular order
        '''
        order = Order.objects.get(id=pk, user=request.user)
        order_items = OrderItem.objects.filter(order=order)
        O_serializer = OrderSerializer(order)
        OI_serializer = OrderItemSerializer(order_items, many=True)
        data = {'order': O_serializer.data, 'order_items': OI_serializer.data}
        return Response(data, status=status.HTTP_200_OK)
    def post(self, request,format=None):
        '''
            Request body:
            address_id, online_payment= false, buy_now=true or false
            if buy_now, then size also

        '''
        address_id = request.data['address_id']
        address = Address.objects.get(pk=address_id, user=request.user)
        
        order = Order(user=request.user, 
        address=address.details+'\n'+address.locality+'\n'+address.landmark+'\n'+address.city+ '\n'+address.pincode, 
        online_payment=False)
        order.save()
        
        #Deciding and creating the order_items related to this order:
        if request.data.get('buy_now', None): #False implies buy_cart
            #request.data will contain product_id, size and quantity
            product = Product.objects.filter(pk=request.data['product_id'])
            if not product.exists():
                order.delete()
                return Response(status=status.HTTP_400_BAD_REQUEST)
            else:
                product = product[0]
            fp = (100-product.discount) * product.price/100
            OrderItem(order=order, name=product.name, 
                                    discount = product.discount, 
                                    initial_price = product.price, 
                                    final_price = fp, 
                                    quantity = request.data['quantity'],
                                    size=request.data['size']).save()
        else:
            #request.user's cart
            cart = Cart.objects.get(user=request.user)
            cps = CartAndProduct.objects.filter(cart = cart)
            if not cps.exists():
                order.delete()
                return Response(status=status.HTTP_400_BAD_REQUEST)
            for item in cps:
                fp = (100-item.product.discount) * item.product.price/100
                OrderItem(order=order, 
                name=item.product.name, initial_price=item.product.price, 
                discount=item.product.discount, final_price=fp, quantity=item.quantity,
                size=item.size).save()
            cps.delete()
            
        return Response(status=status.HTTP_200_OK)  
    def delete(self, request, format=None):
        #Cancel before delivery
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

# class UserPayment(APIView):
#     def get(self, request, format=None):
#         payments = Payment.objects.filter(order__user=request.user)
#         P_serializer = PaymentSerializer(payments, many=True)
#         return Response(P_serializer.data, status.HTTP_200_OK)
# class PaymentCRUD(APIView):
#     def get(self, request, format=None):
#         pk = request.data['pk']
#         payment = Payment.objects.get(pk=pk, order__user=request.user)
#         order = payment.order
#         order_items = OrderItem.objects.filter(order=order)
#         O_serializer = OrderSerializer(order)
#         OI_serializer = OrderItemSerializer(order_items, many=True)
#         P_serializer = PaymentSerializer(payment)
#         data = {'order': O_serializer.data, 'order_items': OI_serializer.data, 'payment':P_serializer.data}
#         return Response(data, status.HTTP_200_OK)
#     def post(self, request, format=None):
#         #Create a payment
#         order = Order.objects.get(pk = request.data['order_id'], user=request.user)
#         if order.online_payment:
#         # Dont send post request to API unless 
#         # online_payment = True, instead create payment obj manually
#             p = Payment(order=order, amount=order.total, amt_paid = order.total, change=0)
#             p.save()
#             #Take money here
#             serializer = PaymentSerializer(p)
#             return Response(serializer.data, status.HTTP_200_OK)

# class UserRefunds(APIView):
#     def get(self, request, format=None):
#         refunds = RefundRequest.objects.filter(order_item__order__user=request.user)
#         R_serializer = RefundSerializer(refunds, many=True)
#         return Response(R_serializer.data, status.HTTP_200_OK)
# class RefundRequestCRUD(APIView):
    # def get(self, request, format=None):
    #     pk = request.data['pk']
    #     refund = RefundRequest.objects.get(pk=pk, order_item__order__user = request.user)
    #     order_item = refund.order_item
    #     R_serializer = RefundSerializer(refund)
    #     OI_serializer = OrderItemSerializer(order_item)
    #     data = {'order_item': OI_serializer.data, 'refund':R_serializer.data}
    #     return Response(data, status.HTTP_200_OK)
    # def post(self, request, format=None):
    #     # if OI has quantity > 1, then to 
    #     # refund n number send quantity with req
    #     # if quantity is not send with request
    #     # refund all
    #     OI_id = request.data['order_item_id']
    #     OI = OrderItem.objects.get(pk=OI_id)
    #     quantity = request.data.get('quantity', OI.quantity)
    #     RefundRequest(order_item=OI, quantity=quantity, amount=OI.final_price * quantity).save()
    #     return Response({'status': 'Request Created'}, status.HTTP_200_OK)
    # def delete(self, request, format=None):
    #     pk = request.data['pk']
    #     refundReq = RefundRequest.objects.get(pk=pk, order_item__order__user=request.user)
    #     if not refundReq.granted:
    #         refundReq.delete()
    #         return Response({'status': 1}, status=status.HTTP_200_OK)
    #     else:
    #         return Response({'status': 0}, status=status.HTTP_200_OK)