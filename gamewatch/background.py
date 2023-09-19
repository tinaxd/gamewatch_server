import os

from celery import Celery

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "gamewatch.settings")

app = Celery(
    "gamewatch",
    broker="redis://localhost:6379",
    backend="redis://localhost:6379",
    include=["ow2db_ip.bg_process"],
)

# Optional configuration, see the application user guide.
app.conf.update(
    result_expires=3600,
)
