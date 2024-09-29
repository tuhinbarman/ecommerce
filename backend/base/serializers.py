from typing import Any, Dict
from rest_framework import serializers
from rest_framework_simplejwt.tokens import Token
from .models import *
from django.contrib.auth.models import User
from rest_framework_simplejwt.serializers import TokenObtainPairSerializer
from rest_framework_simplejwt.tokens import RefreshToken







class MyTokenObtainPairSerializer(TokenObtainPairSerializer):

    @classmethod
    def get_token(cls, user):
        token =  super().get_token(user)
        token['user'] = user.username
        token['message'] = 'hello-world'

        return token
    
    def validate(self, attrs):
        data = super().validate(attrs)
        serializer = UserProfileSerializerWithToken(self.user)
        data.update(serializer.data)  
        return data


class UserProfileSerializer(serializers.ModelSerializer):
    name = serializers.SerializerMethodField(read_only = True)
    _id = serializers.SerializerMethodField(read_only = True)
    isAdmin = serializers.SerializerMethodField(read_only = True)
    class Meta:
        model = User
        fields = ['id','username','name','email', 'isAdmin','_id']

    def get_name(self,obj):
        name = obj.first_name + obj.last_name
        if name == '':
            name = obj.email
        
        return name
    
    def get_isAdmin(self,obj):
        return obj.is_staff
    
    def get__id(self,obj):
        return obj.id
    
class UserProfileSerializerWithToken(UserProfileSerializer):
    token = serializers.SerializerMethodField(read_only=True)

    class Meta : 
        model = User
        fields = ['id','username','name','email', 'isAdmin','_id','token']

    def get_token(self,obj):
        token = RefreshToken.for_user(obj)
        return str(token.access_token)
    
    
class ReviewSerializer(serializers.ModelSerializer):
    class Meta:
        model = Review
        fields = '__all__'   

class ProductSerializer(serializers.ModelSerializer):
    reviews = serializers.SerializerMethodField(read_only=True)
    class Meta:
        model = Product
        fields = '__all__'

    def get_reviews(self,obj):
        reviews = obj.review_set.all()
        review_serialized = ReviewSerializer(reviews,many=True)
        return review_serialized.data



class OrderItemSerializer(serializers.ModelSerializer):
    class Meta:
        model = OrderItem
        fields = '__all__'

class ShippingAddressSerializer(serializers.ModelSerializer):
    class Meta:
        model = ShippingAddress
        fields = '__all__'


class OrderSerializer(serializers.ModelSerializer):
    order_items = serializers.SerializerMethodField(read_only = True)
    shippingAddress = serializers.SerializerMethodField(read_only = True)
    user = serializers.SerializerMethodField(read_only = True)
    class Meta:
        model = Order
        fields = '__all__'

    def get_order_items(self,obj):
        ordersItems = obj.order_items.all()
        serializer = OrderItemSerializer(ordersItems,many=True)
        return serializer.data
    
    def get_shippingAddress(self, obj):
        try:
            address = ShippingAddressSerializer(obj.shippingaddress, many=False).data
        except ShippingAddress.DoesNotExist:
            address = None
        return address

    
    def get_user(self,obj):
        user = obj.user
        serializer = UserProfileSerializer(user,many=False)
        return serializer.data
    


