from django.urls import path
from . import views

urlpatterns  = [
    path('getRoutes/',views.getRoutes,name='getRoutes'),
    path('getProducts/',views.getProducts,name='getProducts'),
    path('getProduct/<int:pk>',views.getProduct,name = 'getProduct'),
    path('user/profile/',views.user_profile,name='user-profile'),
    path('user/login/',views.MyTokenObtainPairView.as_view(),name='token_obtain_pair'),
    
    path('user/register/',views.registerUser,name='register-user'),
    path('user/update/',views.updateUser,name='update-user'),
    path('order/add/',views.addOrderItems,name='add-order-items'),
    path('order/<str:pk>/',views.getOrderById,name='get-order-by-id'),
    path('order/<str:pk>/pay',views.payOrder,name='pay-order'),
    path('order/my_orders',views.getUserOrder,name = 'get-user-orders'),
    path('admin/delete/<str:pk>',views.deleteUser,name= 'delete-user'),
    path('admin/user/<str:pk>',views.getUserByID,name='user-by-id'),
    path('admin/users/',views.get_users,name='users'),
    path('admin/userUpdate/<str:pk>',views.updateUser,name='user-update-by-id'),
    path('admin/products/',views.getAllProductsAdmin,name="get-products-admin"),
    path('admin/product/<str:pk>',views.deleteProduct,name='delete-product'),
    path('admin/createProduct/',views.createProduct,name='create-product'),
    path('admin/updateProduct/<str:pk>',views.updateProduct,name='update-product'),
    path('admin/image/upload/',views.uploadImage,name='image-upload'),
    path('admin/getAllOrders/',views.getAdminOrders,name='get-all-orders'),
    path('order/deliver/<str:pk>',views.deliverOrder,name='deliver-order'),
    path('review/<str:pk>',views.createReview,name='create-review'),
    path('getTopProducts/',views.getTopProducts,name="get-top-products")
]