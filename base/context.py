"""Current tenant context.

The tenant resolved for the running request lives in a `ContextVar`, which is
safe under threads and async alike. `TenantMiddleware` publishes it and
`TenantManager` reads it to scope every query.
"""

from contextlib import contextmanager
from contextvars import ContextVar

_current_tenant = ContextVar('current_tenant', default=None)


def get_current_tenant():
    """Return the tenant of the running request, or None outside a request."""
    return _current_tenant.get()


def set_current_tenant(tenant):
    """Publish the current tenant and return the token needed to reset it."""
    return _current_tenant.set(tenant)


def reset_current_tenant(token):
    """Restore whatever tenant was published before `set_current_tenant`."""
    _current_tenant.reset(token)


@contextmanager
def tenant_context(tenant):
    """Run a block scoped to `tenant`.

    Intended for management commands, Celery tasks and AI tools, which have no
    request to resolve the tenant from. Always restores the previous value.
    """
    token = set_current_tenant(tenant)
    try:
        yield tenant
    finally:
        reset_current_tenant(token)
