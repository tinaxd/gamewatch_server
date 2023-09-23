from django.contrib.auth.decorators import login_required
from django.db.models import Count, OuterRef, Subquery
from django.http import HttpResponse
from django.http.response import HttpResponseBadRequest
from django.shortcuts import render
from django.urls import reverse
from django.views.decorators.cache import cache_control
from rest_framework.decorators import api_view
from rest_framework.exceptions import APIException
from rest_framework.response import Response

from .models import OW2UniqueUser, OW2UserImage, Screenshot
from .serializers import PlayerUpdateSerializer


# Create your views here.
@login_required
def view_screenshots(request):
    scs = Screenshot.objects.only("id").order_by("-created_at").all()[:5]

    images = [
        {
            "path": reverse("ow2db_web:single-screenshot", args=[sc.id]),
            "id": sc.id,
            "sent_by": sc.sent_by,
            "created_at": sc.created_at,
        }
        for sc in scs
    ]

    return render(request, "ow2db_web/list_screenshot.html", {"images": images})


@login_required
def view_players(request):
    subquery = (
        OW2UserImage.objects.values("ow2_user_id")
        .filter(ow2_user_id=OuterRef("id"))
        .annotate(count=Count("*"))
        .values("count")
    )[:1]

    queryset = (
        OW2UniqueUser.objects.annotate(count=Subquery(subquery))
        .values(
            "id",
            "count",
            "first_seen",
            "last_seen",
            "username",
            "comment",
            "rating",
        )
        .order_by("-last_seen")
    )

    players = queryset.all()

    entries = [
        {
            "id": player["id"],
            "path": reverse("ow2db_web:single-player", args=[player["id"]]),
            "first_seen": player["first_seen"],
            "last_seen": player["last_seen"],
            "username": player["username"],
            "comment": player["comment"],
            "rating": player["rating"],
            "count": player["count"],
        }
        for player in players
    ]

    return render(request, "ow2db_web/list_players.html", {"players": entries})


@login_required
@cache_control(public=True, max_age=24 * 60 * 60)
def single_screenshot(request, screenshot_id):
    sc = Screenshot.objects.get(id=screenshot_id)
    return HttpResponse(sc.image.read(), content_type="image/png")


@login_required
@cache_control(public=True, max_age=24 * 60 * 60)
def single_player(request, player_id):
    img = (
        OW2UserImage.objects.filter(ow2_user_id=player_id)
        .order_by("-original_sc__created_at")
        .first()
    )
    return HttpResponse(img.image.read(), content_type="image/png")


@login_required
@api_view(["POST"])
def update_player(request):
    ser = PlayerUpdateSerializer(data=request.data)
    if ser.is_valid():
        ser.save()
        return Response(ser.data)
    else:
        raise APIException(detail=ser.errors, code=400)
