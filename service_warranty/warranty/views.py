from rest_framework.response import Response
from rest_framework.views import APIView
from django.shortcuts import get_object_or_404
import requests
import datetime

from .models import Warranty
from .serializers import WarrantySerializer


class WarrantyView(APIView):
    def get(self, request, item_uid):
        warranty = get_object_or_404(Warranty, item_uid=item_uid)
        return Response({"itemUid": warranty.item_uid, "warrantyDate": warranty.warranty_date,
                         "warrantyStatus": warranty.status}, content_type='application/json',
                        status=200)

    def post(self, request, item_uid):
        json_data = request.data
        json_data.update({"comment": json_data.get('comment', 'Empty')})
        json_data.update({"status": "ON_WARRANTY", "item_uid": item_uid, "warranty_date": datetime.datetime.now()})
        serializer = WarrantySerializer(data=json_data)
        if serializer.is_valid(raise_exception=True):
            warranty_saved = serializer.save()
            return Response(status=204)
        return Response(status=400)

    def delete(self, request, item_uid):
        warranty = get_object_or_404(Warranty, item_uid=item_uid)
        warranty.status = "REMOVED_FROM_WARRANTY"
        warranty.save()
        return Response(status=204)


class WarrantyCheckView(APIView):
    def post(self, request, item_uid):
        available_count = request.data.get("availableCount")
        try:
            warranty = Warranty.objects.get(item_uid=item_uid)
        except Warranty.DoesNotExist:
            return Response({}, status=404, content_type='application/json')
        decision = "REFUSED"
        if warranty.status == "ON_WARRANTY":
            if int(available_count) > 0:
                decision = "RETURN"
            else:
                decision = "FIXING"
        return Response({"itemUid": item_uid, "decision": decision, "warrantyDate": warranty.warranty_date},
                        content_type='application/json')
