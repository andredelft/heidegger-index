python manage.py migrate
python manage.py collectstatic --no-input
python manage.py compress
python manage.py populate_index
python manage.py compilemessages
gunicorn heidegger_index.wsgi:application --bind 0.0.0.0:$1
