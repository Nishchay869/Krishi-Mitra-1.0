from pathlib import Path

from django.conf import settings

_STATIC_ASSETS = (
    'js/register-location.js', 'css/library.css', 'js/chat.js', 'js/spray-details.js',
    'css/weather-planner.css', 'css/mandi.css', 'js/mandi.js', 'css/onboarding.css',
    'js/onboarding.js', 'css/app.css', 'css/premium.css', 'css/theme-contrast.css',
    'css/fertilizer.css', 'css/pests.css', 'frontend/islands.js', 'frontend/islands.css',
    'js/offline-client.js', 'js/offline-ui.js', 'js/service-worker.js', 'offline.html',
    'css/language-fonts.css'
)


def _static_version():
    """Changes whenever a site script/stylesheet changes (including the React islands build),
    so browsers never run stale cached copies."""
    paths = [Path(settings.BASE_DIR) / 'static' / name for name in _STATIC_ASSETS]
    return str(int(max(p.stat().st_mtime for p in paths if p.exists())))


def features(request):
    from accounts.languages import SARVAM_CODES, available_languages
    from .sarvam import VOICE_LANGUAGES
    voice = bool(settings.SARVAM_API_KEY) and SARVAM_CODES.get(getattr(request, 'LANGUAGE_CODE', 'en')) in VOICE_LANGUAGES
    return {
        'VOICE_ENABLED': voice,
        'STATIC_VERSION': _static_version(),
        'AVAILABLE_LANGUAGES': available_languages(),
    }
