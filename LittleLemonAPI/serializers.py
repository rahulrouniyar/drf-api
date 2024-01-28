from rest_framework import serializers
from .models import MenuItem, Category, Cart, Order, OrderItem

from django.contrib.auth.models import User, Group


# class CategorySerializer(serializers.ModelSerializer):
#     class Meta:
#         model = Category
#         # fields = ['id','slug', 'title']
#         fields = ['id']

class MenuItemSerializer(serializers.ModelSerializer):
    # adding foreign key serializer
    # category = serializers.ReadOnlyField(source='category.id')
    # category = CategorySerializer()
    class Meta:
        model = MenuItem
        fields  = ['id', 'title', 'price', 'featured', 'category']

class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ['username', 'email']

class CartSerializer(serializers.ModelSerializer):
    menuitem = serializers.ReadOnlyField(source='menuitem.title')
    class Meta:
        model = Cart
        fields = ['menuitem', 'quantity', 'unit_price', 'price']

class OrderSerializer(serializers.ModelSerializer):
    class Meta:
        model = Order
        fields = ['id', 'user', 'delivery_crew', 'status', 'total', 'date']

class OrderItemSerializer(serializers.ModelSerializer):
    class Meta:
        model = OrderItem
        fields = ['order', 'menuitem', 'quantity', 'unit_price', 'price']


# class CartViewSerializer(serializers.ModelSerializer):                #test
#     class Meta:
#         model = Cart
#         fields = ['user','menuitem','quantity','unit_price','price']