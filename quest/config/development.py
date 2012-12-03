from datetime import timedelta
DEBUG=True
STATIC_URL = '/sitestatic/'
#STATIC_DIR_S3 = 'stage'
DATABASES = {'default': {'ENGINE': 'django.db.backends.sqlite3', 'NAME': '../quest.db', 'USER': '', 'PASSWORD': '', 'HOST': '', 'PORT': '',}}
CELERYD_CONCURRENCY = 16
CELERYD_ETA_SCHEDULER_PRECISION = 0.1
DJKOMBU_POLLING_INTERVAL = 0.1
CELERYBEAT_MAX_LOOP_INTERVAL = 0.1
CELERY_IMPORTS = ("explorer.tasks", )
CELERY_DISABLE_RATE_LIMITS = True
CELERYD_MAX_TASKS_PER_CHILD = 50

CELERYBEAT_SCHEDULE = {
    "recieve-images": {
        "task": "explorer.tasks.get_ready_images",
        "schedule": timedelta(seconds=10),
        "args": ()
    },
    "send-background-items": {
        "task": "explorer.tasks.send_background_items",
        "schedule": timedelta(seconds=60),
        "args": ()
    }
}
