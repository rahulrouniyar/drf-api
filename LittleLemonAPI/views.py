from django.shortcuts import render
from rest_framework.response import Response
from rest_framework.request import Request
from rest_framework import status

#load your base views classes
from rest_framework import viewsets
from rest_framework.views import APIView

# load authentication classes
from rest_framework.authentication import TokenAuthentication

# load permission classes
from .permissions import IsManager, IsDeliveryCrew
from rest_framework.permissions import IsAuthenticated

# load builtin user and group model
from django.contrib.auth.models import User,Group

# load your models here
from .models import MenuItem, Cart, Order, OrderItem

# load your serializers here
from .serializers import MenuItemSerializer, CartSerializer,OrderSerializer, OrderItemSerializer, UserSerializer


# Create your views here.
class MenuItemViewSet(viewsets.ModelViewSet):
    queryset = MenuItem.objects.all()
    serializer_class = MenuItemSerializer

# class CartView(viewsets.ModelViewSet):                #test
#     queryset = Cart.objects.all()
#     serializer_class = CartViewSerializer


class CartViewSet(APIView):
    authentication_classes = [TokenAuthentication]
    permission_classes = [IsAuthenticated]
    
    def get(self, request):
        user = request.user
        try:
            user_details = User.objects.get(id=user.id)
        except User.DoesNotExist:
            return Response({"detail":"User not found."},status=status.HTTP_404_NOT_FOUND)
        
        cart_items = Cart.objects.filter(user_id=user_details.id)
        if cart_items:
            serializer = CartSerializer(cart_items, many=True)
            return Response(serializer.data, status=status.HTTP_200_OK)
        return Response({"detail" : "User doesn't have any items in cart"}, status=status.HTTP_404_NOT_FOUND)

    def post(self, request):
        user = request.user
        menuitem_Id = request.data.get('menuitem')
        quantity = int(request.data.get('quantity'))

        try:
            user_details = User.objects.get(id=user.id)
        except User.DoesNotExist:
            return Response({"detail":"User not found."},status=status.HTTP_404_NOT_FOUND)
        
        menuitem_details = MenuItem.objects.get(id=menuitem_Id)
        unit_price = menuitem_details.price
        price = int(quantity) * unit_price

        cart = Cart(
            user_id=user_details.id,
            menuitem_id=menuitem_Id, 
            quantity=quantity, 
            unit_price=unit_price,
            price=price
            )
        cart.save()
        return Response(status=status.HTTP_201_CREATED)

    def delete(self, request):
        '''Deletes all menu items added to cart for the user'''
        user = request.user
        try:
            user_details = User.objects.get(id=user.id)
        except User.DoesNotExist:
            return Response({"detail":"User not found."},status=status.HTTP_404_NOT_FOUND)
        cart = Cart.objects.filter(user_id=user_details.id)
        cart.delete()
        return Response({"detail" : "All menuitems for user deleted."},status=status.HTTP_200_OK)

# View for order management
class OrderViewSet(APIView):
    authentication_classes = [TokenAuthentication]
    permission_classes = [IsAuthenticated]

    # def get_permissions(self):
    #     if self.request.method == 'GET':
    #         return [IsManager()]
    #     elif self.request.method == 'POST':
    #         return [IsDeliveryCrew()]
    #     return super().get_permissions()
    
    def get(self, request):
        if IsManager().has_permission(request, self):
            # return every orders with respective order item
            orders = Order.objects.all()
            serializer = OrderSerializer(orders, many=True)
            return Response(serializer.data, status=status.HTTP_200_OK)
        elif IsDeliveryCrew().has_permission(request, self):
            orders = Order.objects.filter(delivery_crew = request.user.id)
            if orders:
                serializer = OrderSerializer(orders, many=True)
                return Response(serializer.data, status=status.HTTP_200_OK)
            return Response({"detail": "You don't have any orders assigned."}, status=status.HTTP_404_NOT_FOUND)
        else:
            # view for customer 
            user = request.user
            try:
                user_details = User.objects.get(id=user.id)
            except User.DoesNotExist:
                return Response({"detail":"User not found."},status=status.HTTP_404_NOT_FOUND)
            
            # get items from cart
            cart_items = Cart.objects.filter(user_id=user_details.id)
            if cart_items:
                # create new order id for the user
                order = Order.objects.create(user_id = user_details.id)  
                total = 0.0
                # create order item with new order id
                for item in cart_items:
                    orderitem = OrderItem.objects.create(
                        order_id = order.id, 
                        menuitem_id = item.menuitem_id,
                        quantity = item.quantity,
                        unit_price = item.unit_price,
                        price = item.price
                    )
                    total += float(item.price)
                    item.delete()
                order.total = total
                order.save()
            
            try:
                order = Order.objects.get(user_id = user_details.id)
            except Order.DoesNotExist:
                return Response({"detail":"You don't have any orders yet"}, status=status.HTTP_200_OK)
            if order:
                serializer = OrderSerializer(order)
                # orderitems = OrderItem.objects.filter(order_id = order.id)
                # serializer = OrderItemSerializer(orderitems, many=True)
                return Response(serializer.data, status=status.HTTP_200_OK)      

    def post(self, request):
        return Response({"detail":"Welcome Delivery Crew"},status=status.HTTP_201_CREATED)

# View for user group management
class UserGroupManagement(APIView):
    authentication_classes = [TokenAuthentication]
    permission_classes  = [IsAuthenticated, IsManager]

    def get(self, request):
        managers = User.objects.filter(groups__name='Manager')
        serializer = UserSerializer(managers, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)
    
    def post(self, request):
        username = request.data.get('username')
        manager_group = Group.objects.get(name='Manager')
        user = User.objects.get(username=username)
        user.groups.add(manager_group)
        return Response(status=status.HTTP_201_CREATED)

    def delete(self, request):
        username = request.data.get('username')
        manager_group = Group.objects.get(name='Manager')
        user = User.objects.get(username=username)
        user.groups.remove(manager_group)    
        return Response(status=status.HTTP_200_OK)    
    
# View for delivery group management
class DeliveryGroupManagement(APIView):
    authentication_classes = [TokenAuthentication]
    permission_classes = [IsAuthenticated, IsManager]

    def get(self, request):
        delivery_group = User.objects.filter(groups__name='DeliveryCrew')
        serializer = UserSerializer(delivery_group, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)
    
    def post(self, request):
        username = request.data.get('username')
        delivery_group = Group.objects.get(name='DeliveryCrew')
        user = User.objects.get(username=username)
        user.groups.add(delivery_group)
        return Response(status=status.HTTP_201_CREATED)
    
    def delete(self, request):
        username = request.data.get('username')
        delivery_group = Group.objects.get(name='DeliveryCrew')
        user = User.objects.get(username=username)
        user.groups.remove(delivery_group)
        return Response(status=status.HTTP_200_OK)
