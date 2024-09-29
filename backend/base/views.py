from django.shortcuts import render
from django.http import JsonResponse
# from .products import products
from rest_framework.decorators import api_view
from rest_framework.response import Response
from .models import *
from .serializers import (ProductSerializer,MyTokenObtainPairSerializer,UserProfileSerializer,UserProfileSerializerWithToken,OrderSerializer)
from rest_framework_simplejwt.views import TokenObtainPairView
from rest_framework.decorators import permission_classes
from rest_framework.permissions import (IsAuthenticated,IsAdminUser)
from django.contrib.auth.models import User
from rest_framework import status
from django.core.paginator import Paginator,PageNotAnInteger,EmptyPage

# Create your views here.

class MyTokenObtainPairView(TokenObtainPairView):
    serializer_class = MyTokenObtainPairSerializer


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def user_profile(request):
    user = request.user
    serializer = UserProfileSerializerWithToken(user,many=False)
    return Response(serializer.data)

@api_view(['GET'])
@permission_classes([IsAuthenticated,IsAdminUser])
def get_users(request):
    users = User.objects.all()
    serializer = UserProfileSerializer(users,many=True)
    return Response(serializer.data)

@api_view(['POST'])
def registerUser(request):
   
    data = request.data
    try:
        user = User.objects.create(
            first_name = data['name'],
            email = data['email'],
            username = data['email']
        )
        password = data['password']
        user.set_password(password)
        serializer = UserProfileSerializerWithToken(user,many=False)
        print(serializer.data)
        return Response(serializer.data)
    except:
        message = {'detail' : 'User with this email already exists'}
        return Response(message,status=status.HTTP_400_BAD_REQUEST)
    
@api_view(['PUT'])
@permission_classes([IsAuthenticated])
def updateUser(request):
    user = request.user
    data = request.data
    user.first_name = data['name']
    user.username = data['email']
    user.email = data['email']
    if data['password'] != '':
        user.set_password(data['password'])
    
    user.save()
    
    serializer = UserProfileSerializerWithToken(instance=user,many=False)
    print('serializer-data',serializer.data)
    return Response(serializer.data)


@api_view(['GET'])
def getRoutes(request):
    routes = ['apis/Routes','apis/products','apis/products/:id']
    return Response(routes)

@api_view(['GET'])
def getProducts(request):
    searchquery = request.query_params.get('searchquery',None)
    page = request.query_params.get('page',1)

    products = Product.objects.all()
    if searchquery:
        products = products.filter(name__icontains=searchquery)

    paginator = Paginator(products,2)
    try:
        products = paginator.page(page)
    except PageNotAnInteger:
        products = paginator.page(1)
    except EmptyPage:
        products = paginator.page(paginator.num_pages)
    
    serializer = ProductSerializer(products,many=True)
    return Response({'products' : serializer.data,'page' : page,'num_of_pages' : paginator.num_pages},status=status.HTTP_200_OK)


@api_view(['GET'])
def getProduct(request,pk):
    product = Product.objects.get(_id=pk)
    serializer = ProductSerializer(product,many=False)
    return Response(serializer.data)

@api_view(['POST'])
@permission_classes([IsAuthenticated])
def addOrderItems(request):
    user = request.user
    data = request.data
    orderItems = data['cartItems']


    if orderItems and len(orderItems) == 0 :
        return Response({'details' : 'No Order Items'},status=status.HTTP_400_BAD_REQUEST)
    
    else:
        order = Order.objects.create(
            user = user,
            paymentMethod = data['paymentMethod'],
            taxPrice = data['taxPrice'],
            shippingPrice = data['shippingPrice'],
            totalPrice = data['totalPrice']
        )
        shippingAddress = ShippingAddress.objects.create(
            order = order,
            address = data['shippingAddress']['address'],
            city = data['shippingAddress']['city'],
            postal_code = data['shippingAddress']['postalCode'],
            country = data['shippingAddress']['country'],
        )

        for item in orderItems:
            product = Product.objects.get(_id = item['product'])
            orderItem = OrderItem.objects.create(
                product = product,
                order = order,
                name = product.name,
                qty = item['qty'],
                price = item['price'],
                image = product.image.url
            )

            product.countInStock -= orderItem.qty
            product.save()

        serializer = OrderSerializer(order,many=False)
        return Response({'data' : serializer.data})
    
@api_view(['GET'])
@permission_classes([IsAuthenticated])
def getOrderById(request,pk):
    user = request.user
    if not user:
        return Response({'detail' : 'User not Authenticated'},status=status.HTTP_400_BAD_REQUEST)
    order = Order.objects.get(_id = pk)
    try:
        if user.is_staff or order.user == user : 
            serializer = OrderSerializer(order,many=False)
            return Response(serializer.data,status=status.HTTP_200_OK)
        else:
            return Response({'detail' : 'User is not Authorized'},status=status.HTTP_401_UNAUTHORIZED)
        
    except:
        return Response({'detail' : 'Record not Found'},status=status.HTTP_400_BAD_REQUEST)
    
from datetime import datetime

@api_view(['PUT'])
@permission_classes([IsAuthenticated])
def payOrder(request,pk):
    order = Order.objects.get(_id=pk)
    order.isPaid = True
    order.PaidAt = datetime.now()
    order.save()
    return Response('Payment Successfull',status=status.HTTP_200_OK)

@api_view(['GET'])
@permission_classes([IsAuthenticated])
def getUserOrder(request,format=None):
    try:
        user = request.user
        order = user.order_set.all()
        
        serializer = OrderSerializer(order,many = True)
        print(serializer.data)
        return Response(serializer.data,status=status.HTTP_200_OK)
    except Exception as error:
        return Response( {'error' : error},status=status.HTTP_400_BAD_REQUEST)



@api_view(['DELETE'])
@permission_classes([IsAdminUser])
def deleteUser(request,pk):
    user = User.objects.get(id=pk)
    user.delete()
    return Response({"message" : "Successfully Deleted User"})

@api_view(['GET'])
@permission_classes([IsAdminUser])
def getUserByID(request,pk):
    user = User.objects.get(id=pk)
    serializer = UserProfileSerializer(user,many=False)
    return Response(serializer.data,status=status.HTTP_200_OK)


@api_view(['PUT'])
@permission_classes([IsAdminUser])
def updateUserAdmin(request,pk):
    data = request.data
    user = User.objects.get(id=pk)
    user.first_name = data['name']
    user.username = data['email']
    user.email = data['email']
    user.is_staff = data['isAdmin']
    user.save()
    serializer = UserProfileSerializer(user,many=False)
    return Response(serializer.data,status=status.HTTP_200_OK)


@api_view(['GET'])
@permission_classes([IsAuthenticated,IsAdminUser])
def getAllProductsAdmin(request):
    products = Product.objects.all()
    serializer = ProductSerializer(products,many = True)
    if len(products) == 0:
        return Response({'message' : 'No Products Available','products' : serializer.data},status=status.HTTP_200_OK)
    return Response({'products' : serializer.data},status=status.HTTP_200_OK)


@api_view(['DELETE'])
@permission_classes([IsAuthenticated,IsAdminUser])
def deleteProduct(request,pk):
    product = Product.objects.get(_id = pk)
    if not product:
        return Response({'message' : 'Product Does not Exist'},status=status.HTTP_400_BAD_REQUEST)
    product.delete()
    return Response({'message' : 'Product is successfully deleted'},status=status.HTTP_200_OK)

@api_view(['POST'])
@permission_classes([IsAuthenticated,IsAdminUser])
def createProduct(request):
    user = request.user
    product = Product.objects.create(
        user = user,
        name = 'Sample Name',
        price = 0,
        category='Sample Category',
        description = ''
    )
    product.save()
    serializer = ProductSerializer(product,many=False)
    return Response({'message' : 'Product Successfully Created','product' : serializer.data},status=status.HTTP_201_CREATED)

@api_view(['PUT'])
@permission_classes([IsAuthenticated,IsAdminUser])
def updateProduct(request,pk):
    data = request.data
    product = Product.objects.get(_id=pk)

    product.name = data['name']
    product.price = data['price']
    product.brand = data['brand']
    product.countInStock = data['countInStock']
    product.category = data['category']
    product.description = data['description']
    product.save()

    serializer = ProductSerializer(product,many=False)
    return Response({'data' : serializer.data},status=status.HTTP_200_OK)

@api_view(['POST'])
@permission_classes([IsAuthenticated])
def uploadImage(request):
    data = request.data
    product_id = data['product_id']
    product = Product.objects.get(_id=product_id)
    product.image = request.FILES.get('image')
    product.save()
    print(product.image.url)
    return Response({
        'msg' : 'Image is successfully uploaded',
        'image' : product.image.url
    },status=status.HTTP_200_OK)



@api_view(['GET'])
@permission_classes([IsAuthenticated,IsAdminUser])
def getAdminOrders(request):
    user = request.user
    if not user:
        return Response({'msg':'fail','error' : 'User not Found'},status=status.HTTP_404_NOT_FOUND)
    orders = Order.objects.all()
    if not orders.exists():
        return Response({'msg' : 'fail','data' : []},status=status.HTTP_404_NOT_FOUND)
    serializer = OrderSerializer(orders,many=True)
    return Response({'msg' : 'Success','data' : serializer.data},status=status.HTTP_200_OK)


@api_view(['PUT'])
@permission_classes([IsAuthenticated,IsAdminUser])
def deliverOrder(request,pk):
    try:
        response = {}
        order = Order.objects.get(_id=pk)
        
        if not order:
            response['msg'] = "Fail"
            response['err'] = "Order not Found"
            return Response(response,status = status.HTTP_404_NOT_FOUND)
        order.isDelivered = True
        order.deliveredAt = datetime.now()
        order.save()
        serializer = OrderSerializer(order,many=False)
        response['msg'] = 'Success'
        response['data'] = serializer.data
        return Response(response,status = status.HTTP_200_OK)
    except Exception as e:
        response['msg'] = 'Fail'
        response['err'] = str(e)
        return Response(response,status = status.HTTP_500_INTERNAL_SERVER_ERROR)
    

@api_view(['POST'])
@permission_classes([IsAuthenticated])
def createReview(request,pk):
    try:
        user = request.user
        product = Product.objects.get(_id=pk)
        data = request.data
        # import pdb;pdb.set_trace()
        print(user.first_name)
        reviewExists = product.review_set.filter(user=user).exists()
        if reviewExists:
            return Response({'error' : 'Product already reviewed','msg' : 'Fail'},status=status.HTTP_400_BAD_REQUEST)
        elif data['rating'] == 0:
            return Response({'error' : 'Please provide a rating','msg' : 'Fail'},status = status.HTTP_400_BAD_REQUEST)
        else:
            review = Review.objects.create(
                product = product,
                user = user,
                name = user.first_name,
                rating = data['rating'],
                comment = data['comment']
            )

            review.save()

            numofReviews = product.numsReviews + 1
            product.numsReviews = numofReviews
            reviews = product.review_set.all()
            total = sum([review.rating for review in reviews])
            product.ratings = total/numofReviews
            
            product.save()

            return Response({'msg' : 'Success' , 'data' : 'Review successfully added' },status=status.HTTP_201_CREATED)

    except Exception as e:
        return Response({'error' : str(e),'msg' : 'Fail'},status=status.HTTP_500_INTERNAL_SERVER_ERROR)

@api_view(['GET'])
def getTopProducts(request):
    try:
        products = Product.objects.filter(ratings__gte=4).order_by('-ratings')[:3]
        serializer = ProductSerializer(products, many=True)
        
        if len(serializer.data) == 0:
            return Response({'msg': 'Fail', 'error': 'No records found'}, status=status.HTTP_404_NOT_FOUND)
        
        return Response({'msg': 'Success', 'data': serializer.data}, status=status.HTTP_200_OK)
    
    except Exception as e:
        return Response({'msg': 'Fail', 'error': str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)



    
    



        






   
    
