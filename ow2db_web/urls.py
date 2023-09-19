from django.urls import path

from . import views

app_name = "ow2db_web"

urlpatterns = [
    path("screenshots", views.view_screenshots, name="list-screenshots"),
    path(
        "screenshot/<int:screenshot_id>",
        views.single_screenshot,
        name="single-screenshot",
    ),
    path("players", views.view_players, name="list-players"),
    path("player/<int:player_id>", views.single_player, name="single-player"),
    path("player", views.update_player, name="update-player"),
]
