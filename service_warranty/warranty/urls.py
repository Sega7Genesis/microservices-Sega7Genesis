from django.urls import path

from . import views

urlpatterns = [
    path('/<uuid:item_uid>', views.WarrantyView.as_view(), name='warranty'),
    path('/<uuid:item_uid>/warranty', views.WarrantyCheckView.as_view(), name='warranty_check')
]