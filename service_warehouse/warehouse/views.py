import uuid
import requests
import os
from rest_framework.response import Response
from rest_framework.views import APIView
from django.shortcuts import get_object_or_404
from django.http import QueryDict
from .my_cb import my_circle_breaker
from .models import Items, OrderItem
from .serializers import ItemsSerializer, OrderItemSerializer

warranty_url = os.environ.get("WARRANTY_URL", "volosatov-warranty.herokuapp.com")
warranty_cb = my_circle_breaker(3, 60)

class ItemsView(APIView):
    def get(self, request):
        items = Items.objects.all()
        serializer = ItemsSerializer(items, many=True)
        return Response(serializer.data)

    def post(self, request):
        json_data = request.data
        if isinstance(json_data, QueryDict):
            json_data = json_data.dict()
        item = Items.objects.filter(model=json_data.get("model"), size=json_data.get("size"))[0]
        if item and item.available_count > 0:
            json_data.update({'canceled': False, 'item_id': item.id, 'order_item_uid': uuid.uuid1(),
                              "order_uid": json_data.get('orderUid')})
            serializer = OrderItemSerializer(data=json_data)
            if serializer.is_valid(raise_exception=True):
                # reduce items count in warranty
                item.available_count -= 1
                item.save()
                serializer.save()
                return Response({'orderItemUid': json_data.get('order_item_uid'),
                                 "orderUid": json_data.get("orderUid"), "model": item.model, "size": item.size},
                                status=200, content_type='application/json')
        return Response(status=400)


class OrderItemView(APIView):
    def get(self, request, orderItemUid):
        order_item = get_object_or_404(OrderItem, order_item_uid=orderItemUid)
        item = get_object_or_404(Items, id=order_item.item_id)
        return Response({"model": item.model, "size": item.size, "item_id": item.id},
                        content_type='application/json')

    def delete(self, request, orderItemUid):
        order_item = get_object_or_404(OrderItem, order_item_uid=orderItemUid)
        if not order_item.canceled:
            order_item.canceled = True
            #order_item.save()
            # increase items count in warranty
            item = get_object_or_404(Items, id=order_item.item_id)
            item.available_count += 1
            #item.save()
            #ORDER
            warranty = warranty_cb.do_request(f"http://{warranty_url}/api/v1/warranty/{orderItemUid}", http_method='delete')
            if warranty.status_code == 404:
                return Response({'message': f'cant delete warranty with orderItemUid {orderItemUid}'}, status=404,
                                content_type='application/json')
            if warranty.status_code == 503:
                return warranty
            #url = f"http://{warranty_url}/api/v1/warranty/{orderItemUid}"
            #requests.delete(url)
            order_item.save()
            item.save()
        return Response(status=204)


class OrderItemWarrantyView(APIView):
    def post(self, request, orderItemUid):
        url = f"http://{warranty_url}/api/v1/warranty/{orderItemUid}/warranty"
        order_item = get_object_or_404(OrderItem, order_item_uid=orderItemUid)
        item = get_object_or_404(Items, id=order_item.item_id)
        response = warranty_cb.do_request(url, http_method='post', context={'availableCount': item.available_count})
        if response.status_code == 404:
            return Response({'message': f"Warranty not found for itemUid \'{orderItemUid}\'"}, status=404,
                            content_type='application/json')
        if response.status_code == 503:
            return response
        #response = requests.post(url, {'availableCount': item.available_count})
        if response.status_code == 404:
            return Response({"message": f"Warranty not found for itemUid \'{orderItemUid}\'"},
                            status=404, content_type="application/json")
        return Response(response.data, content_type='application/json')
