import os

from celery import Celery
from celery.schedules import crontab
from django_structlog.celery.steps import DjangoStructLogInitStep

from alfred.utils import read_env_var

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "alfred.settings")

app = Celery("alfred")

app.config_from_object("django.conf:settings", namespace="CELERY")

app.autodiscover_tasks()


app.steps["worker"].add(DjangoStructLogInitStep)  # type: ignore
app.conf.worker_hijack_root_logger = False


@app.on_after_finalize.connect  # type: ignore
def setup_periodic_tasks(sender, **kwargs):
    import alfred.tasks  # noqa


env = read_env_var("ENVIRONMENT")
if env == "PRODUCTION":
    schedule = crontab(minute="0", hour="6-22", day_of_week="mon-fri")
else:
    schedule = 60 * 60 * 24  # s = 1d

app.conf.beat_schedule = {
    "pull_opportunities": {
        "task": "alfred.tasks.process_pull_opportunities",
        "one_off": True,
        "enabled": False,
        "schedule": schedule,
    },
    "sync_opportunities": {
        "task": "alfred.tasks.process_sync_opportunities",
        "schedule": schedule,
    },
    "pull_volunteerform": {
        "task": "alfred.tasks.process_pull_volunteerform",
        "one_off": True,
        "enabled": False,
        "schedule": schedule,
    },
    "sync_volunteerform": {
        "task": "alfred.tasks.process_sync_volunteerform",
        "schedule": schedule,
    },
    "old_pull_opportunities": {
        "task": "alfred.tasks.process_opportunities",
        "enabled": False,
        "schedule": schedule,
    },
}
