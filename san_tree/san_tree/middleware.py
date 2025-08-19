from django.conf import settings
from django.shortcuts import redirect
from django.urls import resolve, Resolver404

class RequireLoginMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        # Allow access to static, media, and service worker files
        if request.path.startswith(settings.STATIC_URL) or \
           request.path.startswith(settings.MEDIA_URL) or \
           request.path in ['/serviceworker.js', '/manifest.json']:
            return self.get_response(request)

        exempt_view_names = [
            'login',
            'home',
            'register',
            'admin:login',
            'password_reset',
            'password_reset_done',
            'password_reset_confirm',
            'password_reset_complete',
        ]

        try:
            match = resolve(request.path)
            view_name = match.view_name
        except Resolver404:
            # Let unresolved paths pass through (they may be handled elsewhere)
            return self.get_response(request)

        if not request.user.is_authenticated and view_name not in exempt_view_names:
            return redirect(f'{settings.LOGIN_URL}?next={request.path}')
        
        return self.get_response(request)
