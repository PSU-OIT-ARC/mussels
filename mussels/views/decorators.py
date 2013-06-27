from functools import wraps
from django.http import HttpResponseRedirect
from django.core.urlresolvers import reverse

def staff_member_required(fn):
    @wraps(fn)
    def wrapper(request, *args, **kwargs):
        if not request.user.is_staff:
            return HttpResponseRedirect(reverse("accounts-login"))
        return fn(request, *args, **kwargs)

    return wrapper
