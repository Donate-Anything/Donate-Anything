docker-compose -f local.yml down --volumes
docker-compose -f local.yml run --rm django python manage.py migrate
docker-compose -f local.yml run --rm django python manage.py create_item_data
docker-compose -f local.yml run --rm django python manage.py create_charity_data
docker-compose -f local.yml run --rm django python manage.py create_forum_data
echo "Creating username test, pw test, email test@test.com"
docker-compose -f local.yml run --rm django python manage.py shell -c "from django.contrib.auth import get_user_model; get_user_model().objects.create_superuser('test', 'test@test.com', 'test'); from allauth.account.models import EmailAddress; EmailAddress.objects.all().update(verified=True, primary=True)"
echo "Done"
