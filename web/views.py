import datetime

from django.contrib.admin.views.decorators import staff_member_required
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import User
from django.core import serializers
from django.db import transaction
from django.db.models import Sum
from django.db.models.expressions import F
from django.db.models.functions import Extract
from django.http import HttpResponse
from django.shortcuts import redirect, render
from django.urls import reverse
from django.views.decorators.cache import cache_control

from . import models
from .forms import LinkForm, LoginForm, RegisterForm

# Create your views here.


@cache_control(public=True, max_age=600)
def rank(request):
    return render(request, "web/rank.html", {})


@cache_control(public=True, max_age=600)
def level(request):
    return render(request, "web/level.html", {})


@cache_control(public=True, max_age=600)
def apexability(request):
    recent_records = models.PlayHistory.objects.all().order_by("-start_time")[:20]

    # calculate total playing duration of each player for each year, month and game
    monthly_playing_time = (
        models.PlayHistory.objects.filter(
            # stop_time is not null
            stop_time__isnull=False,
        )
        .values(
            # player
            "player",
            # year and month
            "start_time__year",
            "start_time__month",
            # game
            "played_game",
        )
        .annotate(
            player_display_name=F("player__display_name"),
            game_name=F("played_game__name"),
            # sum of duration
            duration=Extract(Sum(F("stop_time") - F("start_time")), "epoch"),
        )
    ).all()
    # print(monthly_playing_time)
    monthly_records = []
    for record in monthly_playing_time:
        # print(record)
        monthly_records.append(
            {
                "player": record["player_display_name"],
                "year": record["start_time__year"],
                "month": record["start_time__month"],
                "game": record["game_name"],
                "duration": record["duration"],
            }
        )

    return render(
        request,
        "web/apexability.html",
        {
            "recent_records": recent_records,
            "monthly_records": monthly_records,
        },
    )


@login_required
def account(request):
    username = request.user.username
    link = models.UserLink.objects.filter(user=request.user).first()
    if link is None:
        player_name = None
        discord_names = None
    else:
        player_name = link.player.display_name
        discord_names = None
    is_staff = request.user.is_staff
    return render(
        request,
        "web/account.html",
        {
            "account_name": username,
            "player_name": player_name,
            "staff": is_staff,
            "discord_names": discord_names,
        },
    )


def logout_account(request):
    logout(request)
    return redirect(reverse("web:login-account"))


def register_account(request):
    if request.method == "POST":
        form = RegisterForm(request.POST)
        if form.is_valid():
            username = form.cleaned_data["username"]
            password = form.cleaned_data["password"]
            u = User()
            u.username = username
            u.set_password(password)
            u.save()
            return redirect(reverse("web:account"))
    else:
        form = RegisterForm()

    return render(request, "web/createuser.html", {"form": form})


def login_account(request):
    error_message = None
    if request.method == "POST":
        form = LoginForm(request.POST)
        if form.is_valid():
            username = form.cleaned_data["username"]
            password = form.cleaned_data["password"]
            user = authenticate(request, username=username, password=password)
            if user is not None:
                login(request, user)
                return redirect(reverse("web:account"))
            else:
                error_message = "Login failed"
    else:
        form = LoginForm()
        error_message = None

    return render(
        request, "web/login.html", {"form": form, "error_message": error_message}
    )


@login_required
def link_account(request):
    if request.method == "POST":
        form = LinkForm(request.POST)
        if form.is_valid():
            player = form.cleaned_data["player"]
            if player is not None:
                link = models.PendingUserLink.objects.filter(user=request.user).first()
                if link is None:
                    link = models.PendingUserLink(
                        user=request.user,
                        player=player,
                        requested_time=datetime.datetime.now(),
                    )
                else:
                    link.player = player
                link.save()
                return redirect(reverse("web:account"))
            else:
                # TODO: error handling
                return HttpResponse(status=500)
    else:
        form = LinkForm()

    return render(request, "web/account_link.html", {"form": form})


@staff_member_required
def link_approve(request):
    if request.method == "POST":
        action = request.POST["action"]  # 'reject' or 'approve'
        username = request.POST["username"]
        player_id = int(request.POST["player_id"])

        target_user = User.objects.filter(username=username).first()
        if target_user is None:
            return HttpResponse(status=500)
        player = models.Player.objects.filter(id=player_id).first()
        if player is None:
            return HttpResponse(status=500)
        p = models.PendingUserLink.objects.filter(user=target_user).first()
        if p is None:
            return HttpResponse(status=500)
        with transaction.atomic():
            p.delete()
            if action == "approve":
                link = models.UserLink.objects.filter(user=target_user).first()
                if link is None:
                    link = models.UserLink(user=target_user, player=player)
                else:
                    link.player = player
                link.save()

    pendings = models.PendingUserLink.objects.all()
    return render(request, "web/account_link_approve.html", {"pendings": pendings})


@login_required
def manual_check(request):
    # return a string that states this feature is not usable yet.
    return HttpResponse("This feature is not available now.")


def root(request):
    return redirect("web:level")
