python manage.py migrate
python manage.py populate
python manage.py collectstatic --no-input
gunicorn heidegger_index.wsgi:application --bind 0.0.0.0:$1
