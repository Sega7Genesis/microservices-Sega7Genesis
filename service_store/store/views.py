import requests
import os
from rest_framework.response import Response
from rest_framework.views import APIView
from django.shortcuts import get_object_or_404
from .my_cb import my_circle_breaker
from .models import User
from .serializers import UserSerializer
from .rabbit import Uses_Q
from datetime import datetime


order_url = os.environ.get("ORDER_URL", "volosatov-order.herokuapp.com")
order_cb = my_circle_breaker(3, 60)
warranty_cb = my_circle_breaker(3, 60)

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
        orders = order_cb.do_request(f"http://{order_url}/api/v1/orders/{user.user_uuid}", http_method='get')
        #orders = requests.get(f"http://{order_url}/api/v1/orders/{user.user_uuid}")
        if orders.status_code == 404:
            return Response({'message': f'user with user_uuid {user_id} not found in orders'}, status=404, content_type='application/json')
        if orders.status_code == 503:
            return orders
        return Response(orders.data, content_type="application/json")


class StorePurchase(APIView):
    def post(self, request, user_id):
        user = get_object_or_404(User, user_uuid=user_id)
        json_data = request.data
        model = json_data.get('model')
        size = json_data.get('size')
        #TODO new_order as orders
        new_order = order_cb.do_request(f"http://{order_url}/api/v1/orders/{user.user_uuid}", http_method='post', context={"model": model, "size": size})
        #new_order = requests.post(f"http://{order_url}/api/v1/orders/{user.user_uuid}",
        #                          {"model": model, "size": size}).json()
        headers = {"Location": f"/{new_order.data.get('orderUid')}"}
        if new_order.status_code == 404:
            return Response({'message': 'cant create new order'}, status=404, content_type='application/json')
        if new_order.status_code == 503:
            return new_order
        return Response(status=201, headers=headers)


class StoreOrderDetail(APIView):
    def get(self, request, user_id, order_id):
        user = get_object_or_404(User, user_uuid=user_id)
        order_detail = order_cb.do_request(f"http://{order_url}/api/v1/orders/{user_id}/{order_id}", http_method='get')
        #order_detail = requests.get(f"http://{order_url}/api/v1/orders/{user_id}/{order_id}")
        if order_detail.status_code == 404:
            return Response({'message': f'cant find order with order_id {order_id} '}, status=404, content_type='application/json')
        if order_detail.status_code == 503:
            return order_detail
        return Response(order_detail.data, content_type="application/json")


class StoreRefund(APIView):
    def delete(self, request, user_id, order_id):
        order = order_cb.do_request(f"http://{order_url}/api/v1/orders/{order_id}", http_method='delete')
        #order = requests.delete(f"http://{order_url}/api/v1/orders/{order_id}")
        if order.status_code == 404:
            return Response({'message': f'cant delete order with order_id {order_id}'}, status=404, content_type='application/json')
        if order.status_code == 503:
            return order
        return Response(status=order.status_code)


class StoreWarranty(APIView):
    def post(self, request, user_id, order_id):
        user = get_object_or_404(User, user_uuid=user_id)
        warranty = warranty_cb.do_request(f"http://{order_url}/api/v1/orders/{order_id}/warranty", http_method='post')
        if warranty.status_code == 404:
            return Response({'message': f'cant find warranty on order with order_id {order_id} '}, status=404, content_type='application/json')
        if warranty.status_code == 503:
            #TODO add request to queue order_id user_id datetime.now
            with Uses_Q as mq:
                mq.send({'time': datetime.now, 'user_id': user_id, 'order_id': order_id})
            return Response({'message': f'warranty is unavailable< but your request is on queue'})
        #warranty = requests.post(f"http://{order_url}/api/v1/orders/{order_id}/warranty").json()

        warranty = warranty.data
        #TODO for req in
        old_results = []
        with Uses_Q as mq:
            for req in mq.take():
                result = warranty_cb.do_request(f"http://{order_url}/api/v1/orders/{req.get('order_id')}/warranty",
                                                http_method='post')
                req.update(result.data)
                old_results.append(req)
        #добавил старые результаты для видимости
        warranty.update({"orderUid": order_id, 'old_results': old_results})
        return Response(warranty, content_type="application/json")
