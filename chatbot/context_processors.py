from django.conf import settings


def features(request):
    return {'VOICE_ENABLED': bool(settings.SARVAM_API_KEY)}
