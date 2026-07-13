from django.conf import settings
from django.test import SimpleTestCase


class SessionSettingsTests(SimpleTestCase):
    def test_session_cookie_is_not_marked_secure_in_debug(self):
        self.assertFalse(settings.SESSION_EXPIRE_AT_BROWSER_CLOSE)
        self.assertIsInstance(settings.SESSION_COOKIE_SECURE, bool)
        self.assertFalse(settings.SESSION_COOKIE_SECURE)
