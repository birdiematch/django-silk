from functools import wraps

from django.contrib.auth.decorators import login_required
from django.core.exceptions import PermissionDenied
from django.utils.decorators import available_attrs

from silk.config import SilkyConfig


def login_possibly_required(function=None, **kwargs):
    if not SilkyConfig().SILKY_AUTHENTICATION:
        return function

    if kwargs.get("login_url") is None:
        kwargs["login_url"] = SilkyConfig().SILKY_LOGIN_URL

    return login_required(function, **kwargs)


def permissions_possibly_required(function=None):
    if SilkyConfig().SILKY_AUTHORISATION:
        actual_decorator = user_passes_test(
            SilkyConfig().SILKY_PERMISSIONS
        )
        if function:
            return actual_decorator(function)
        return actual_decorator
    return function


def user_passes_test(test_func):
    def decorator(view_func):
        @wraps(view_func, assigned=available_attrs(view_func))
        def _wrapped_view(request, *args, **kwargs):
            if test_func(request.user):
                return view_func(request, *args, **kwargs)
            else:
                raise PermissionDenied

        return _wrapped_view

    return decorator
