web: newrelic-admin run-program python quest/manage.py runserver "0.0.0.0:$PORT" --noreload
celeryd: python quest/manage.py collectstatic --ignore venv --noinput; python quest/manage.py celeryd -E -B --loglevel=WARNING -I explorer.tasks