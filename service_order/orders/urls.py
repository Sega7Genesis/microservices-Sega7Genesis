from django.urls import path

from . import views

urlpatterns = [
    path('/<uuid:userUid>', views.OrdersView.as_view(), name='orders'),
    path('/<uuid:userUid>/<uuid:orderUid>', views.OrderIdView.as_view(), name='orders_with_id'),
    path('/<uuid:orderUid>/warranty', views.OrderWarranty.as_view(), name='order_warranty')
]