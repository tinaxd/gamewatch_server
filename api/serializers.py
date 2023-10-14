from datetime import datetime

from rest_framework import serializers
from rest_framework.exceptions import APIException

from ow2db_ip.bg_process import process_screenshot_by_id
from ow2db_web.models import Screenshot
from web import models as wm


class ObjectNotFoundError(APIException):
    status_code = 404
    default_detail = "Object not found"

    def __init__(self, object_name: str) -> None:
        self.detail = f"Specified {object_name} not found"


class LevelUpdateCreateSerializer(serializers.Serializer):
    in_game_name = serializers.CharField()
    old_level = serializers.IntegerField(required=False)
    new_level = serializers.IntegerField()
    time = serializers.DateTimeField()

    def validate_in_game_name(self, value):
        if not wm.InGameName.objects.filter(in_game_name=value).exists():
            raise ObjectNotFoundError("in_game_name")
        return value

    def create(self, validated_data):
        player = (
            wm.InGameName.objects.filter(in_game_name=validated_data["in_game_name"])
            .first()
            .player
        )
        wm.LevelUpdate.objects.create(
            player=player,
            old_level=validated_data["old_level"],
            new_level=validated_data["new_level"],
            time=validated_data["time"],
        )
        return validated_data


class RankUpdateCreateSerializer(serializers.Serializer):
    in_game_name = serializers.CharField()
    old_rank = serializers.IntegerField(required=False)
    new_rank = serializers.IntegerField()
    rank_type = serializers.ChoiceField([("trio", "Trio"), ("arena", "Arena")])
    time = serializers.DateTimeField()
    old_rank_name = serializers.CharField()
    new_rank_name = serializers.CharField()

    def validate_in_game_name(self, value):
        if not wm.InGameName.objects.filter(in_game_name=value).exists():
            raise ObjectNotFoundError("in_game_name")
        return value

    def create(self, validated_data):
        player = (
            wm.InGameName.objects.filter(in_game_name=validated_data["in_game_name"])
            .first()
            .player
        )
        wm.RankUpdate.objects.create(
            player=player,
            old_rank=validated_data["old_rank"],
            new_rank=validated_data["new_rank"],
            time=validated_data["time"],
            rank_type=validated_data["rank_type"],
            old_rank_name=validated_data["old_rank_name"],
            new_rank_name=validated_data["new_rank_name"],
        )
        return validated_data


class ApexabilityCheckSerializer(serializers.Serializer):
    in_game_name = serializers.CharField()
    type = serializers.ChoiceField([("start", "Start"), ("stop", "Stop")])
    time = serializers.DateTimeField()
    game_name = serializers.CharField()

    def validate_in_game_name(self, value):
        if not wm.InGameName.objects.filter(in_game_name=value).exists():
            raise ObjectNotFoundError("in_game_name")
        return value

    def validate_game_name(self, value):
        if not wm.Game.objects.filter(name=value).exists():
            raise ObjectNotFoundError("game_name")
        return value

    def create(self, validated_data):
        player = (
            wm.InGameName.objects.filter(in_game_name=validated_data["in_game_name"])
            .first()
            .player
        )
        game = wm.Game.objects.filter(name=validated_data["game_name"]).first()

        if validated_data["type"] == "start":
            # check if there is an existing start entry
            existing_start = wm.PlayHistory.objects.filter(
                player=player, stop_time=None
            ).first()
            # if there is, ignore the request
            if existing_start:
                return validated_data
            else:
                # add a new start entry
                wm.PlayHistory.objects.create(
                    player=player,
                    played_game=game,
                    start_time=validated_data["time"],
                    stop_time=None,
                )
                return validated_data
        elif validated_data["type"] == "stop":
            # check if there is an existing start entry
            existing_start = wm.PlayHistory.objects.filter(
                player=player, stop_time=None
            ).first()
            # if there is, add a stop entry
            if existing_start:
                existing_start.stop_time = validated_data["time"]
                existing_start.save()
                return validated_data
            else:
                # check the latest already-stopped entry
                already_stopped = (
                    wm.PlayHistory.objects.filter(player=player)
                    .order_by("-stop_time")
                    .first()
                )
                if already_stopped is None:
                    # ignore the request
                    return validated_data
                else:
                    # extend the stop time
                    # game may be different, but that's fine
                    already_stopped.stop_time = validated_data["time"]
                    already_stopped.save()
                    return validated_data
        else:
            # this is not possible
            # as already validated
            raise Exception("Invalid type")


class CompatLevelUpdateSerializer(serializers.Serializer):
    player_name = serializers.CharField()
    old_rank = serializers.IntegerField(required=False)
    new_rank = serializers.IntegerField()
    timestamp = serializers.IntegerField()

    def validate_player_name(self, value):
        if not wm.InGameName.objects.filter(in_game_name=value).exists():
            raise ObjectNotFoundError("player_name")
        return value

    def create(self, validated_data):
        player = (
            wm.InGameName.objects.filter(in_game_name=validated_data["player_name"])
            .first()
            .player
        )
        time = datetime.fromtimestamp(validated_data["timestamp"])
        wm.LevelUpdate.objects.create(
            player=player,
            old_level=validated_data["old_rank"],
            new_level=validated_data["new_rank"],
            time=time,
        )
        return validated_data


class CompatRankUpdateSerializer(serializers.Serializer):
    player_name = serializers.CharField()
    old_rank = serializers.IntegerField(required=False)
    new_rank = serializers.IntegerField()
    rank_type = serializers.ChoiceField([("trio", "Trio"), ("arena", "Arena")])
    timestamp = serializers.IntegerField()
    old_rank_name = serializers.CharField()
    new_rank_name = serializers.CharField()

    def validate_player_name(self, value):
        if not wm.InGameName.objects.filter(in_game_name=value).exists():
            raise ObjectNotFoundError("player_name")
        return value

    def create(self, validated_data):
        player = (
            wm.InGameName.objects.filter(in_game_name=validated_data["player_name"])
            .first()
            .player
        )
        time = datetime.fromtimestamp(validated_data["timestamp"])
        wm.RankUpdate.objects.create(
            player=player,
            old_rank=validated_data["old_rank"],
            new_rank=validated_data["new_rank"],
            time=time,
            rank_type=validated_data["rank_type"],
            old_rank_name=validated_data["old_rank_name"],
            new_rank_name=validated_data["new_rank_name"],
        )
        return validated_data


class LevelUpdateSerializer(serializers.ModelSerializer):
    level = serializers.IntegerField(source="new_level")
    player = serializers.CharField(max_length=50, source="player.display_name")

    class Meta:
        model = wm.LevelUpdate
        fields = ["player", "level", "time"]


class RankUpdateSerializer(serializers.ModelSerializer):
    rank = serializers.IntegerField(source="new_rank")
    rank_name = serializers.CharField(source="new_rank_name")
    player = serializers.CharField(max_length=50, source="player.display_name")

    class Meta:
        model = wm.RankUpdate
        fields = ["player", "time", "rank", "rank_name", "rank_type"]


class CheckSerializer(serializers.Serializer):
    player = serializers.CharField(max_length=50)
    entry_type = serializers.CharField(max_length=5)
    time = serializers.DateTimeField()
    game_name = serializers.CharField(max_length=64, allow_null=True)


class OW2DBUploadSerializer(serializers.Serializer):
    image = serializers.FileField()
    sent_by = serializers.CharField(max_length=100)

    def create(self, validated_data):
        upload = Screenshot(
            image=validated_data["image"], sent_by=validated_data["sent_by"]
        )
        upload.save()

        bg_task = process_screenshot_by_id.delay(upload.id)
        bg_task.forget()

        return validated_data
