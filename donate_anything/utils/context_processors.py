from django.conf import settings


def settings_context(_request):
    return {"MEDIA_URL": settings.MEDIA_URL}
