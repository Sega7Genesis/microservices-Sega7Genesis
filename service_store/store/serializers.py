from rest_framework import serializers

from .models import User


class UserSerializer(serializers.Serializer):
    id = serializers.IntegerField(read_only=True)
    name = serializers.CharField(max_length=255, required=True, allow_null=False)
    user_uuid = serializers.UUIDField()

    def create(self, validated_data):
        return User.objects.create(**validated_data)

    def update(self, instance, validated_data):
        instance.name = validated_data.get('name', instance.name)
        instance.user_uuid = validated_data.get('user_uuid', instance.user_uuid)
        return instance

    def validate(self, data):
        if not data.get('name'):
            raise serializers.ValidationError()
        return data
