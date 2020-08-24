# Removing the volume because we might be creating new tables or modifying old ones
docker-compose -f local.yml down --volumes
echo "Creating username test, pw test, email test@test.com with some other test data"
docker-compose -f local.yml run --rm django python manage.py shell -c "from django.core.management import call_command; call_command('migrate'); call_command('create_item_data'); call_command('create_charity_data'); call_command('create_forum_data'); from django.contrib.auth import get_user_model; user = get_user_model().objects.create_superuser('test', 'test@test.com', 'test'); from allauth.account.models import EmailAddress; EmailAddress.objects.create(user=user, email=user.email, verified=True, primary=True)"
echo "Done: username test, pw test, email test@test.com"
