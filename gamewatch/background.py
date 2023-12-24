import os

from celery import Celery

from .settings import REDIS_URL

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "gamewatch.settings")

app = Celery(
    "gamewatch",
    broker=REDIS_URL,
    backend=REDIS_URL,
    include=["ow2db_ip.bg_process"],
)

# Optional configuration, see the application user guide.
app.conf.update(
    result_expires=3600,
)
