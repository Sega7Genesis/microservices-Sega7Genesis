import uuid
import datetime
import os
import requests
from rest_framework.response import Response
from rest_framework.views import APIView
from django.shortcuts import get_object_or_404
from django.http import QueryDict

from .models import Order
from .serializers import OrderSerializer


warehouse_url = os.environ.get("WAREHOUSE_URL", "enine-warehouse.herokuapp.com")
warranty_url = os.environ.get("WARRANTY_URL", "enine-warranty.herokuapp.com")


class OrdersView(APIView):
    def get(self, request, userUid):
        orders = Order.objects.all().filter(user_uid=userUid)
        response = [{"orderUid": order.order_uid, "itemUid": order.item_uid, "status": order.status}
                    for order in orders]
        return Response(response, content_type="application/json")

    def post(self, request, userUid):
        json_data = request.data
        if isinstance(json_data, QueryDict):
            json_data = json_data.dict()

        json_data.update({"user_uid": userUid})
        json_data.update({'order_date': datetime.datetime.now(), 'status': 'PAID', 'order_uid': uuid.uuid1()})

        response = requests.get(f'http://{warehouse_url}/api/v1/warehouse', json_data).json()
        model = json_data.get('model')
        size = json_data.get('size')
        needed_item = [x for x in response if x.get('model') == model and
                       x.get('size') == size and x.get('available_count') > 0]

        if needed_item:
            response = requests.post(f'http://{warehouse_url}/api/v1/warehouse',
                                     {'model': model, 'size': size, 'orderUid': json_data.get('order_uid')}).json()
            json_data.update({"item_uid": response.get('orderItemUid')})

            # MOVED FROM WAREHOUSE STR 34
            url = f"http://{warranty_url}/api/v1/warranty/{json_data.get('item_uid')}"
            requests.post(url)

            serializer = OrderSerializer(data=json_data)
            if serializer.is_valid(raise_exception=True):
                order_saved = serializer.save()
                return Response({'orderUid': json_data.get('order_uid')},
                                status=200, content_type="application/json")
        return Response(status=400)

    def delete(self, request, userUid):
        # Because i hate django
        order_uid = userUid
        order = get_object_or_404(Order, order_uid=order_uid)
        requests.delete(f'http://{warehouse_url}/api/v1/warehouse/{order.item_uid}')
        order.delete()
        return Response(status=204)


class OrderIdView(APIView):
    def get(self, request, userUid, orderUid):
        order = get_object_or_404(Order, order_uid=orderUid, user_uid=userUid)
        order_item = requests.get(f'http://{warehouse_url}/api/v1/warehouse/{order.item_uid}').json()
        items = requests.get(f'http://{warehouse_url}/api/v1/warehouse').json()
        needed_item = [x for x in items if x.get('id') == order_item.get("item_id")][0]
        warranty = requests.get(f'http://{warranty_url}/api/v1/warranty/{order.item_uid}').json()
        return Response({"orderUid": order.order_uid, "itemUid": order.item_uid, "status": order.status,
                         "date": order.order_date, "model": needed_item.get("model"), "size": needed_item.get("size"),
                        "warrantyDate": warranty.get("warrantyDate"), "warrantyStatus": warranty.get("warrantyStatus")},
                        content_type="application/json")


class OrderWarranty(APIView):
    def post(self, request, orderUid):
        order = get_object_or_404(Order, order_uid=orderUid)
        if order:
            url = f'http://{warehouse_url}/api/v1/warehouse/{order.item_uid}/warranty'
            response = requests.post(url).json()
            return Response(response, content_type="application/json")
        return Response(status=404, content_type="application/json")
