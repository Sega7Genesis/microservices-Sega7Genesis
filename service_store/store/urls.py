from django.urls import path

from . import views

urlpatterns = [
    path('', views.UserView.as_view(), name='users'),
    path('/<uuid:user_id>/orders', views.StoreOrders.as_view(), name='store_orders'),
    path('/<uuid:user_id>/purchase', views.StorePurchase.as_view(), name='store_purchase'),
    path('/<uuid:user_id>/<uuid:order_id>', views.StoreOrderDetail.as_view(), name='store_order_detail'),
    path('/<uuid:user_id>/<uuid:order_id>/refund', views.StoreRefund.as_view(), name='store_refund'),
    path('/<uuid:user_id>/<uuid:order_id>/warranty', views.StoreWarranty.as_view(), name='store_warranty')
]