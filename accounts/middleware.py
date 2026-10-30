from django.middleware.locale import LocaleMiddleware
from django.utils import translation

from .languages import available_languages


class FarmerLanguageMiddleware(LocaleMiddleware):
    """The saved farmer preference takes precedence over browser/cookie language."""

    async_capable = False

    def __call__(self, request):
        # Do not leak one farmer's language to subsequent work on the same thread.
        with translation.override(translation.get_language()):
            return super().__call__(request)

    def process_request(self, request):
        language = request.COOKIES.get('django_language', 'en')
        if request.user.is_authenticated:
            language = request.user.profile.preferred_language
        language = language if language in dict(available_languages()) else 'en'
        translation.activate(language)
        request.LANGUAGE_CODE = language

    def process_response(self, request, response):
        response = super().process_response(request, response)
        if request.user.is_authenticated:
            response.set_cookie('django_language', request.LANGUAGE_CODE,
                                max_age=365 * 24 * 60 * 60, samesite='Lax',
                                secure=request.is_secure())
        return response
