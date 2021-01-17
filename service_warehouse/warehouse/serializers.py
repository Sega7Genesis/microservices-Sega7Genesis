from rest_framework import serializers

from .models import Items, OrderItem


class ItemsSerializer(serializers.Serializer):
    id = serializers.IntegerField(read_only=True)
    available_count = serializers.IntegerField()
    model = serializers.CharField(max_length=255)
    size = serializers.CharField(max_length=255)

    def create(self, validated_data):
        return Items.objects.create(**validated_data)

    def update(self, instance, validated_data):
        instance.available_count = validated_data.get('available_count', instance.available_count)
        instance.model = validated_data.get('model', instance.model)
        instance.size = validated_data.get('size', instance.size)
        instance.save()
        return instance

    def validate(self, data):
        if not data.get('model'):
            raise serializers.ValidationError()
        return data


class OrderItemSerializer(serializers.Serializer):
    canceled = serializers.BooleanField()
    order_item_uid = serializers.UUIDField()
    order_uid = serializers.UUIDField()
    item_id = serializers.IntegerField()

    def create(self, validated_data):
        return OrderItem.objects.create(**validated_data)

    def update(self, instance, validated_data):
        instance.canceled = validated_data.get('canceled', instance.canceled)
        instance.order_item_uid = validated_data.get('order_item_uid', instance.order_item_uid)
        instance.order_uid = validated_data.get('order_uid', instance.order_uid)
        instance.item_id = validated_data.get('item_id', instance.item_id)
        instance.save()
        return instance

    def validate(self, data):
        if not data.get('item_id'):
            raise serializers.ValidationError()
        if not data.get('order_uid'):
            raise serializers.ValidationError()
        if not data.get('order_item_uid'):
            raise serializers.ValidationError()
        return data
