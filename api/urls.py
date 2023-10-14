from django.urls import path

from . import views

urlpatterns = [
    path("register/level", views.LevelUpdateView.as_view(), name="register-level"),
    path("register/rank", views.RankUpdateView.as_view(), name="register-rank"),
    path(
        "register/check",
        views.ApexabilityCheckView.as_view(),
        name="register-apexability",
    ),
    path(
        "compat/level/register",
        views.CompatLevelUpdateView.as_view(),
        name="register-level-compat",
    ),
    path(
        "compat/rank/register",
        views.CompatRankUpdateView.as_view(),
        name="register-rank-compat",
    ),
    path("view/level", views.level, name="view-level"),
    path("view/rank", views.rank, name="view-rank"),
    # path("view/check", views.check, name="view-check"),
    path("ow2db/upload", views.OW2DBImageUpload.as_view(), name="ow2db-upload"),
    path("game/is_tracked", views.is_tracked_game, name="game-is-tracked"),
    path(
        "game/<game_name>/emoji_name", views.get_game_emoji_name, name="game-emoji-name"
    ),
    path(
        "game/reverse_game_from_emoji",
        views.reverse_game_from_emoji,
        name="reverse-game-from-emoji",
    ),
    path("game/emoji_list", views.get_game_emoji_list, name="game-emoji-list"),
]
