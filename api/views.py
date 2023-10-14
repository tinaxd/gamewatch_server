from django.core.cache import cache
from django.http import JsonResponse
from django.views.decorators.cache import cache_control
from rest_framework import generics, mixins, status
from rest_framework.decorators import api_view
from rest_framework.response import Response
from rest_framework.views import APIView

from web import models as wm

from . import cache_keys as ck
from . import serializers as ser

# Create your views here.


class LevelUpdateView(APIView):
    def post(self, request):
        serializer = ser.LevelUpdateCreateSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            cache.delete(ck.LEVEL_UPDATE_KEY)
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(status=status.HTTP_400_BAD_REQUEST)


class RankUpdateView(APIView):
    def post(self, request):
        serializer = ser.RankUpdateCreateSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            cache.delete(ck.RANK_UPDATE_KEY)
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(status=status.HTTP_400_BAD_REQUEST)


class ApexabilityCheckView(APIView):
    def post(self, request):
        serializer = ser.ApexabilityCheckSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            cache.delete(ck.GAME_CHECK_KEY)
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(status=status.HTTP_400_BAD_REQUEST)


class CompatLevelUpdateView(APIView):
    def post(self, request):
        serializer = ser.CompatLevelUpdateSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            cache.delete(ck.LEVEL_UPDATE_KEY)
            return Response(status=status.HTTP_200_OK)
        return Response(status=status.HTTP_400_BAD_REQUEST)


class CompatRankUpdateView(APIView):
    def post(self, request):
        serializer = ser.CompatRankUpdateSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            cache.delete(ck.RANK_UPDATE_KEY)
            return Response(status=status.HTTP_200_OK)
        return Response(status=status.HTTP_400_BAD_REQUEST)


@cache_control(public=True, max_age=60)
@api_view(["GET"])
def rank(request):
    cache_res = cache.get(ck.RANK_UPDATE_KEY)
    if cache_res:
        return JsonResponse(cache_res, safe=False)

    rank_raw = wm.RankUpdate.objects.all()
    serializer = ser.RankUpdateSerializer(rank_raw, many=True)
    cache.set(ck.RANK_UPDATE_KEY, serializer.data)
    return JsonResponse(serializer.data, safe=False)


@cache_control(public=True, max_age=60)
@api_view(["GET"])
def level(request):
    cache_res = cache.get(ck.LEVEL_UPDATE_KEY)
    if cache_res:
        return JsonResponse(cache_res, safe=False)

    level_raw = wm.LevelUpdate.objects.all()
    serializer = ser.LevelUpdateSerializer(level_raw, many=True)
    cache.set(ck.LEVEL_UPDATE_KEY, serializer.data)
    return JsonResponse(serializer.data, safe=False)


@cache_control(public=True, max_age=60)
@api_view(["GET"])
def check(request):
    cache_res = cache.get(ck.GAME_CHECK_KEY)
    if cache_res:
        return JsonResponse(cache_res, safe=False)

    raw = wm.ApexabilityCheck.objects.order_by("-time").all()
    serializer = ser.CheckSerializer(raw, many=True)
    cache.set(ck.GAME_CHECK_KEY, serializer.data)
    return JsonResponse(serializer.data, safe=False)


class OW2DBImageUpload(mixins.CreateModelMixin, generics.GenericAPIView):
    serializer_class = ser.OW2DBUploadSerializer

    def post(self, request, *args, **kwargs):
        return self.create(request, *args, **kwargs)


@api_view(["GET"])
def is_tracked_game(request):
    game_name = request.GET.get("game_name", None)
    if game_name is None:
        return Response(status=status.HTTP_400_BAD_REQUEST)

    game = wm.Game.objects.filter(name=game_name).first()
    if game is None:
        return JsonResponse({"is_tracked": False})
    else:
        return JsonResponse({"is_tracked": True})


@api_view(["GET"])
def get_game_emoji_name(request, game_name):
    game = wm.Game.objects.filter(name=game_name).first()
    if game is None or game.emoji_name is None:
        return Response(status=status.HTTP_404_NOT_FOUND)
    else:
        return JsonResponse({"emoji_name": game.emoji_name})


@api_view(["GET"])
def reverse_game_from_emoji(request):
    emoji_name = request.GET.get("emoji_name", None)
    if emoji_name is None:
        return Response(status=status.HTTP_400_BAD_REQUEST)

    game = wm.Game.objects.filter(emoji_name=emoji_name).first()
    if game is None:
        return Response(status=status.HTTP_404_NOT_FOUND)
    else:
        return JsonResponse({"game_name": game.name})


@api_view(["GET"])
def get_game_emoji_list(request):
    games = wm.Game.objects.filter(emoji_name__isnull=False).all()
    return JsonResponse({"emoji_names": [game.emoji_name for game in games]})
