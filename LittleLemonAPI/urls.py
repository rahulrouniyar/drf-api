from django.urls import path,include
from . import views
from rest_framework import routers

router = routers.DefaultRouter(trailing_slash=False)
router.register(r'menu-items',views.MenuItemViewSet)
# router.register(r'cart',views.CartView)

# URL Patterns
urlpatterns = [
    path('',include(router.urls)),
    path('cart/menu-items/', views.CartViewSet.as_view()),
    path('group/manager/users/', views.UserGroupManagement.as_view(), name='managergroup' ),
    path('group/delivery-crew/users/', views.DeliveryGroupManagement.as_view(), name='deliverygroup' ),
    path('orders/', views.OrderViewSet.as_view(), name='orders'),
    path('orders/<int:orderId>/', views.SingleOrderViewSet.as_view(), name='orderitem-detail'),
]

