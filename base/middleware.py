import logging

from django.contrib.auth import get_user_model, logout

from base.context import reset_current_tenant, set_current_tenant

logger = logging.getLogger(__name__)


def user_model_has_tenant():
    """Whether the active user model already carries a `tenant` field.

    The tenant field lands with the custom user model in Sprint 2. Until then
    the middleware resolves no tenant and, crucially, does not log anyone out.
    """
    return any(field.name == 'tenant' for field in get_user_model()._meta.fields)


class TenantMiddleware:
    """Resolve the tenant of the authenticated user and publish it in context.

    Runs after `AuthenticationMiddleware`, which is what puts `request.user`
    in place. The ContextVar is always reset on the way out so a recycled
    worker thread never inherits the previous request's tenant.
    """

    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        tenant = self.resolve_tenant(request)
        request.tenant = tenant

        token = set_current_tenant(tenant)
        try:
            return self.get_response(request)
        finally:
            reset_current_tenant(token)

    def resolve_tenant(self, request):
        user = getattr(request, 'user', None)

        if user is None or not user.is_authenticated:
            return None

        # Superusers operate across tenants through the admin and the
        # `all_tenants` manager, so they are never bound to one.
        if user.is_superuser:
            return None

        if not user_model_has_tenant():
            return None

        tenant = getattr(user, 'tenant', None)

        if tenant is None or not tenant.is_active:
            logger.warning(
                'Usuario %s autenticado sem corretora ativa; encerrando a sessao.',
                user.pk,
            )
            logout(request)
            return None

        return tenant
