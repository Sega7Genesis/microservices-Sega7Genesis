import uuid
import datetime
import os
import requests
from rest_framework.response import Response
from rest_framework.views import APIView
from django.shortcuts import get_object_or_404
from django.http import QueryDict
from .my_cb import my_circle_breaker
from .models import Order
from .serializers import OrderSerializer


warehouse_url = os.environ.get("WAREHOUSE_URL", "volosatov-warehouse.herokuapp.com")
warranty_url = os.environ.get("WARRANTY_URL", "volosatov-warranty.herokuapp.com")
#TODO add 2 circle breaker objects
warehouse_cb = my_circle_breaker(3, 60)
warranty_cb = my_circle_breaker(3, 60)

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
            #response = requests.post(f'http://{warehouse_url}/api/v1/warehouse',
            #                         {'model': model, 'size': size, 'orderUid': json_data.get('order_uid')}).json()
            warehouse_response = warehouse_cb.do_request(f'http://{warehouse_url}/api/v1/warehouse', http_method='post', context={'model': model, 'size': size, 'orderUid': json_data.get('order_uid')})
            if warehouse_response.status_code == 404:
                return Response({'message': f' cant find item at warehouse'}, status=404,
                                content_type='application/json')
            if warehouse_response.status_code == 503:
                return warehouse_response
            json_data.update({"item_uid": response.get('orderItemUid')})

            # MOVED FROM WAREHOUSE STR 34

            url = f"http://{warranty_url}/api/v1/warranty/{json_data.get('item_uid')}"
            warranty_response = warranty_cb.do_request(url, http_method='post')
            if warranty_response.status_code == 404:
                return Response({'message': f' cant find warranty on item'}, status=404,
                                content_type='application/json')
            if warranty_response.status_code == 503:
                return warranty_response
            #requests.post(url)

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
        warehouse_delete = warehouse_cb.do_request(f'http://{warehouse_url}/api/v1/warehouse/{order.item_uid}', http_method='delete')
        if warehouse_delete.status_code == 404:
            return Response({'message': f' cant delete item with order item uid {order.item_uid} from warehouse'}, status=404,
                            content_type='application/json')
        if warehouse_delete.status_code == 503:
            return warehouse_delete
        #requests.delete(f'http://{warehouse_url}/api/v1/warehouse/{order.item_uid}')
        order.delete()
        return Response(status=204)


class OrderIdView(APIView):
    def get(self, request, userUid, orderUid):
        result = {}
        order = get_object_or_404(Order, order_uid=orderUid, user_uid=userUid)
        result.update({"orderUid": order.order_uid, "itemUid": order.item_uid, "status": order.status,
                        "date": order.order_date})
        #order_item = requests.get(f'http://{warehouse_url}/api/v1/warehouse/{order.item_uid}').json()
        order_item = warehouse_cb.do_request(f'http://{warehouse_url}/api/v1/warehouse/{order.item_uid}', http_method='get')
        if order_item.status_code == 503:
            result.update({"model": None, "size": None})
        else:
            items = warehouse_cb.do_request(f'http://{warehouse_url}/api/v1/warehouse', http_method='get')
            if items.status_code == 503:
                result.update({"model": None, "size": None})
            else:
                needed_item = [x for x in items if x.get('id') == order_item.get("item_id")][0]
                result.update({"model": needed_item.get("model"), "size": needed_item.get("size")})
        #items = requests.get(f'http://{warehouse_url}/api/v1/warehouse').json()

        #needed_item = [x for x in items if x.get('id') == order_item.get("item_id")][0]
        #warranty = requests.get(f'http://{warranty_url}/api/v1/warranty/{order.item_uid}').json()
        warranty = warranty_cb.do_request(f'http://{warranty_url}/api/v1/warranty/{order.item_uid}', http_method='get')
        if warranty.status_code == 404:
            return Response({'message': f' cant find warranty on item with order item uid {order.item_uid}'}, status=404,
                            content_type='application/json')
        if warranty.status_code == 503:
            result.update({"warrantyDate": warranty.get("warrantyDate"), "warrantyStatus": warranty.get("warrantyStatus")},
                        content_type="application/json")
        return Response({"orderUid": order.order_uid, "itemUid": order.item_uid, "status": order.status,
                         "date": order.order_date, "model": needed_item.get("model"), "size": needed_item.get("size"),
                        "warrantyDate": warranty.get("warrantyDate"), "warrantyStatus": warranty.get("warrantyStatus")},
                        content_type="application/json")
        #
        #if t

class OrderWarranty(APIView):
    def post(self, request, orderUid):
        order = get_object_or_404(Order, order_uid=orderUid)
        if order:
            url = f'http://{warehouse_url}/api/v1/warehouse/{order.item_uid}/warranty'
            response = warehouse_cb.do_request(url, http_method='post')
            if response.status_code == 404:
                return Response({'message': f' cant find warranty on order with {order.item_uid}'},
                                status=404,
                                content_type='application/json')
            if response.status_code == 503:
                return response
            #response = requests.post(url).json()
            return Response(response, content_type="application/json")
        return Response(status=404, content_type="application/json")
