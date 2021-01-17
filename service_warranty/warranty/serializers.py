from rest_framework import serializers

from .models import Warranty


class WarrantySerializer(serializers.Serializer):
    id = serializers.IntegerField(read_only=True)
    comment = serializers.CharField(max_length=1024)
    item_uid = serializers.UUIDField()
    status = serializers.CharField(max_length=255)
    warranty_date = serializers.DateTimeField()

    def create(self, validated_data):
        return Warranty.objects.create(**validated_data)

    def update(self, instance, validated_data):
        instance.comment = validated_data.get('comment', instance.comment)
        instance.item_uid = validated_data.get('item_uid', instance.item_uid)
        instance.status = validated_data.get('status', instance.status)
        instance.warranty_date = validated_data.get('warranty_date', instance.warranty_date)
        instance.save()
        return instance

    def validate(self, data):
        if not data.get('item_uid'):
            raise serializers.ValidationError()
        return data
