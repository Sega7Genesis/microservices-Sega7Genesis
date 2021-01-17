from rest_framework import serializers

from .models import Order


class OrderSerializer(serializers.Serializer):
    id = serializers.IntegerField(read_only=True)
    item_uid = serializers.UUIDField()
    order_date = serializers.DateTimeField(required=False)
    order_uid = serializers.UUIDField(required=False)
    status = serializers.CharField(max_length=255, required=False)
    user_uid = serializers.UUIDField()

    def create(self, validated_data):
        return Order.objects.create(**validated_data)

    def update(self, instance, validated_data):
        instance.item_uid = validated_data.get('item_uid', instance.item_uid)
        instance.order_date = validated_data.get('order_date', instance.order_date)
        instance.order_uid = validated_data.get('order_uid', instance.order_uid)
        instance.status = validated_data.get('status', instance.status)
        instance.user_uid = validated_data.get('user_uid', instance.user_uid)
        instance.save()
        return instance

    def validate(self, data):
        if not data.get('order_uid'):
            raise serializers.ValidationError()
        return data
