from copy import copy

from django.core.exceptions import ImproperlyConfigured
from django.utils import six

from silk.singleton import Singleton


def default_permissions(user):
    if user:
        return user.is_staff
    return False


def default_requst_model_edit(silk_request_model, request_object):
    return silk_request_model


class SilkyConfig(six.with_metaclass(Singleton, object)):
    defaults = {
        'SILKY_DYNAMIC_PROFILING': [],
        'SILKY_IGNORE_PATHS': [],
        'SILKY_HIDE_COOKIES': True,
        'SILKY_IGNORE_QUERIES': [],
        'SILKY_META': False,
        'SILKY_AUTHENTICATION': False,
        'SILKY_AUTHORISATION': False,
        'SILKY_PERMISSIONS': default_permissions,
        'SILKY_MAX_RECORDED_REQUESTS': 10 ** 4,
        'SILKY_MAX_RECORDED_REQUESTS_CHECK_PERCENT': 10,
        'SILKY_MAX_REQUEST_BODY_SIZE': -1,
        'SILKY_MAX_RESPONSE_BODY_SIZE': -1,
        'SILKY_INTERCEPT_PERCENT': 100,
        'SILKY_INTERCEPT_FUNC': None,
        'SILKY_PYTHON_PROFILER': False,
        'SILKY_STORAGE_CLASS': 'silk.storage.ProfilerResultStorage',

        # BM enhancements
        'SILKY_DATABASE_NAME': 'default',
        'SILKY_LOGIN_URL': None,
        'SILKY_EDIT_REQUEST_MODEL_FUNCTION': default_requst_model_edit,
        'SILKY_LOG_USER_AGENT': False
    }

    def _setup(self):
        from django.conf import settings

        options = {option: getattr(settings, option) for option in dir(settings) if option.startswith('SILKY')}
        self.attrs = copy(self.defaults)
        self.attrs['SILKY_PYTHON_PROFILER_RESULT_PATH'] = settings.MEDIA_ROOT
        self.attrs.update(options)

        if self.attrs["SILKY_DATABASE_NAME"] != "default":
            self._check_database_routers(settings.DATABASE_ROUTERS)

    def _check_database_routers(self, routers):
        """
        Checks the given list of router module paths for occurance of SilkDBRouter.
        Raises ImproperlyConfigured, if not present.
        """
        silk_router_present = False

        for r in routers:
            if r == "silk.routers.SilkDBRouter":
                silk_router_present = True

        if not silk_router_present:
            raise ImproperlyConfigured("When using 'SILKY_DATABASE_NAME', also add 'silk.routers.SilkDBRouter' to your 'DATABASE_ROUTERS'.")

    def __init__(self):
        super(SilkyConfig, self).__init__()
        self._setup()

    def __getattr__(self, item):
        return self.attrs.get(item, None)

    def __setattribute__(self, key, value):
        self.attrs[key] = value
