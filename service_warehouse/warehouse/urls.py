from django.urls import path

from . import views

urlpatterns = [
    path('', views.ItemsView.as_view(), name='items'),
    path('/<uuid:orderItemUid>', views.OrderItemView.as_view(), name='order_item'),
    path('/<uuid:orderItemUid>/warranty', views.OrderItemWarrantyView.as_view(), name='order_warranty')
]
