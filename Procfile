web: newrelic-admin run-program python quest/manage.py runserver "0.0.0.0:$PORT" --noreload
celeryd: python quest/manage.py collectstatic -i flags -i jquery -i tiny_mce-3.5b3 -i icons -i jquery-ui-1.8.13.custom -i contrib -i admin_tools -i images/ext -i adgalery -i media -i admin -i blueprint --noinput; python quest/manage.py celeryd -E -B --loglevel=WARNING -I explorer.tasks