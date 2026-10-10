from pathlib import Path

from django.conf import settings

_STATIC_ASSETS = ('js/chat.js', 'css/app.css')


def _static_version():
    """Changes whenever chat.js or app.css changes, so browsers never run stale cached copies."""
    mtimes = [(Path(settings.BASE_DIR) / 'static' / name).stat().st_mtime for name in _STATIC_ASSETS]
    return str(int(max(mtimes)))


def features(request):
    return {'VOICE_ENABLED': bool(settings.SARVAM_API_KEY), 'STATIC_VERSION': _static_version()}
