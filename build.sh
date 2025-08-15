set -o errexit

pip install -r requirements.txt

python manage.py collectstatic --no-input

python manage.py migrate

if [ "$CREATE_SUPERUSER" = "True" ]; then
    echo "✅ Creating superuser from env vars..."
    python manage.py createsuperuser --no-input
else
    echo "🔕 CREATE_SUPERUSER is not enabled. Skipping superuser creation."
fi