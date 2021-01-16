from django.http import HttpResponse, JsonResponse, Http404
from rest_framework.views import APIView
from rest_framework.permissions import AllowAny
from rest_framework.response import Response
from rest_framework import status
from .serializers import OrderItemSerializer, OrderSerializer
from ..models import Order, OrderItem
from Accounts.models import CartAndProduct, Address, Cart
from Products.models import Product
from django.contrib.auth import authenticate
import datetime
import stripe
from django.conf import settings
from Accounts.models import User
stripe.api_key = settings.STRIPE_SK

class UserOrders(APIView):
    def get(self, request, format=None):
        orders = Order.objects.filter(user=request.user)
        O_serializer = OrderSerializer(orders, many=True)
        return Response(O_serializer.data, status.HTTP_200_OK)

import json
from django.http import HttpResponse

# Using Django
from django.views.decorators.csrf import csrf_exempt
endpoint_secret = settings.STRIPE_WEBHOOK_SECRET
@csrf_exempt
def stripe_webhook(request):
    payload = request.body
    sig_header = request.META['HTTP_STRIPE_SIGNATURE']
    event = None

    try:
        event = stripe.Event.construct_from(json.loads(payload), sig_header, endpoint_secret)
    except ValueError as e:
        return HttpResponse(status=400)
    except stripe.error.SignatureVerificationError as e:
        return HttpResponse(status=400)
    
    if event.type=='checkout.session.completed':
        # print(event.data.object)
        if event.data.object.metadata.get('buy_now', None):
            print('buy_now', event.data.object.metadata.buy_now)
            print(event.data.object)
            user = User.objects.get(email=event.data.object.customer_details.email)
            o = Order(user=user, address=event.data.object.metadata.address, online_payment=True, paid=True)
            o.save()
            p = Product.objects.get(pk= event.data.object.metadata.product_id)
            oi = OrderItem(order=o, product=p, 
                initial_price = float(event.data.object.metadata.price), 
                final_price=float(event.data.object.metadata.final_price),
                quantity=int(event.data.object.metadata.quantity)
            ).save()

        else:
            print(event.data.object)
        #Generate payment and order here
    else:
        print('Unhandled event type {}'.format(event.type))

    return HttpResponse(status=200)
class OnlinePayment(APIView):
    def post(self, request):
        if request.data['buy_now']:
            product = Product.objects.get(pk=request.data['product_id'])
            address = Address.objects.get(pk=request.data['address_id'], user=request.user)
            session = stripe.checkout.Session.create(
                payment_method_types=['card'],
                customer_email=request.user.email,
                line_items=[{
                    'price_data': {
                        'currency': 'inr',
                        'product_data': {'name': product.name},
                        'unit_amount': (100-product.discount) * product.price, #in paise.
                    },
                    'quantity': request.data['quantity'],
                }],
                mode='payment',
                success_url=settings.FRONT_END_HOST+'/product/'+request.data['product_id'],
                cancel_url=settings.FRONT_END_HOST+'/product/'+request.data['product_id'],
                metadata={
                    "buy_now": True,
                    "product_id": request.data['product_id'],
                    "quantity": request.data['quantity'],
                    "discount": product.discount,
                    "price": product.price,
                    "final_price": ((100-product.discount) * product.price)/100, #in rupees
                    "address": address.details+' \n '+address.locality+' \n '+address.landmark+' \n '+address.city+ ' \n '+address.pincode 
                }
            )
            return Response({"sess_id":session.id})
        else:
            pass
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
            address_id, online_payment=true or false, buy_now=true or false

            Instead of signals to generate payment, we can also do if online_payment is true:
            Payment(request.data['stripe_transaction_id'] , ... ).save()
            in this method itself.
        '''
        address_id = request.data['address_id']
        address = Address.objects.get(pk=address_id, user=request.user)
        
        order = Order(user=request.user, 
        address=address.details+' \n '+address.locality+' \n '+address.landmark+' \n '+address.city+ ' \n '+address.pincode, 
        online_payment=False)
        order.save()
        
        #Deciding and creating the order_items related to this order:
        if request.data.get('buy_now', None): #False implies buy_cart
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