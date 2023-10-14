import datetime

from django.contrib.admin.views.decorators import staff_member_required
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import User
from django.db import transaction
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
    return render(request, "web/apexability.html", {})


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
