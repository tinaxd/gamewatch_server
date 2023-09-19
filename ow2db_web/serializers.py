from rest_framework import serializers
from rest_framework.exceptions import ValidationError
from rest_framework.response import Response

from . import models


class ObjectNotFoundError(ValidationError):
    status_code = 404
    default_detail = "Object not found."
    default_code = "not_found"


class PlayerUpdateSerializer(serializers.Serializer):
    player_id = serializers.IntegerField()
    username = serializers.CharField(max_length=100, allow_blank=True)
    comment = serializers.CharField(max_length=1000, allow_blank=True)

    def validate_player_id(self, value):
        if not models.OW2UniqueUser.objects.filter(id=value).exists():
            raise ObjectNotFoundError()
        return value

    def create(self, validated_data):
        unique_user = models.OW2UniqueUser.objects.get(id=validated_data["player_id"])
        unique_user.username = (
            validated_data["username"]
            if "username" in validated_data
            else unique_user.username
        )
        unique_user.comment = (
            validated_data["comment"]
            if "comment" in validated_data
            else unique_user.comment
        )
        unique_user.save()
        return validated_data
