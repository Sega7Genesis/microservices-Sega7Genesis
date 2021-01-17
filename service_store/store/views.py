import requests
import os
from rest_framework.response import Response
from rest_framework.views import APIView
from django.shortcuts import get_object_or_404

from .models import User
from .serializers import UserSerializer


order_url = os.environ.get("ORDER_URL", "enine-order.herokuapp.com")


class UserView(APIView):
    def get(self, request):
        users = User.objects.all()
        serializer = UserSerializer(users, many=True)
        return Response(serializer.data)

    def post(self, request):
        json_data = request.data
        serializer = UserSerializer(data=json_data)
        if serializer.is_valid(raise_exception=True):
            user_saved = serializer.save()
            return Response(status=201)
        return Response(status=400)


class StoreOrders(APIView):
    def get(self, request, user_id):
        user = get_object_or_404(User, user_uuid=user_id)
        orders = requests.get(f"http://{order_url}/api/v1/orders/{user.user_uuid}")
        return Response(orders.json(), content_type="application/json")


class StorePurchase(APIView):
    def post(self, request, user_id):
        user = get_object_or_404(User, user_uuid=user_id)
        json_data = request.data
        model = json_data.get('model')
        size = json_data.get('size')
        new_order = requests.post(f"http://{order_url}/api/v1/orders/{user.user_uuid}",
                                  {"model": model, "size": size}).json()
        headers = {"Location": f"/{new_order.get('orderUid')}"}
        return Response(status=201, headers=headers)


class StoreOrderDetail(APIView):
    def get(self, request, user_id, order_id):
        user = get_object_or_404(User, user_uuid=user_id)
        order_detail = requests.get(f"http://{order_url}/api/v1/orders/{user_id}/{order_id}")
        return Response(order_detail.json(), content_type="application/json")


class StoreRefund(APIView):
    def delete(self, request, user_id, order_id):
        order = requests.delete(f"http://{order_url}/api/v1/orders/{order_id}")
        return Response(status=order.status_code)


class StoreWarranty(APIView):
    def post(self, request, user_id, order_id):
        user = get_object_or_404(User, user_uuid=user_id)
        warranty = requests.post(f"http://{order_url}/api/v1/orders/{order_id}/warranty").json()
        warranty.update({"orderUid": order_id})
        return Response(warranty, content_type="application/json")
