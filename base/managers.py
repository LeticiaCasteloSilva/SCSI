from django.db import models

from base.context import get_current_tenant


class TenantQuerySet(models.QuerySet):
    """QuerySet with an explicit tenant filter, usable outside a request."""

    def for_tenant(self, tenant):
        return self.filter(tenant=tenant)


class TenantManager(models.Manager.from_queryset(TenantQuerySet)):
    """Default manager of every domain model: scopes queries to the tenant.

    When there is no tenant in context the manager returns an empty queryset
    instead of every row. Failing closed means a forgotten middleware or a
    stray query outside a request yields nothing, never another tenant's data.

    Code that legitimately needs to cross tenants — the superuser admin,
    management commands, AI tools — must use the `all_tenants` manager and
    pass the tenant explicitly, or wrap the block in `base.context.
    tenant_context`.
    """

    def get_queryset(self):
        queryset = super().get_queryset()
        tenant = get_current_tenant()
        if tenant is None:
            return queryset.none()
        return queryset.filter(tenant=tenant)
