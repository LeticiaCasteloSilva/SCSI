from django.contrib.auth.mixins import LoginRequiredMixin
from django.core.exceptions import PermissionDenied

from base.constants import Role


class TenantRequiredMixin(LoginRequiredMixin):
    """Base mixin of every authenticated CBV.

    Guarantees there is a tenant in context and assigns it on create/update,
    so `tenant` is never accepted from the POST payload.
    """

    def dispatch(self, request, *args, **kwargs):
        response = super().dispatch(request, *args, **kwargs)

        # LoginRequiredMixin already redirected an anonymous user; only an
        # authenticated user reaching here without a tenant is an error.
        if request.user.is_authenticated and getattr(request, 'tenant', None) is None:
            if not request.user.is_superuser:
                raise PermissionDenied('Usuário sem corretora associada.')

        return response

    def form_valid(self, form):
        if hasattr(form.instance, 'tenant_id'):
            form.instance.tenant = self.request.tenant
        return super().form_valid(form)


class RolePermissionMixin:
    """Narrow the queryset to what the user's role is allowed to see.

    Applied on top of the tenant filter, never instead of it:

    - `OWNER`    sees everything in the tenant
    - `AGENT`    sees their own records and those of their producers
    - `PRODUCER` sees only their own records

    Views set `agent_field` / `producer_field` to the path that reaches those
    foreign keys on the model. A field left as None is simply not filtered.
    """

    agent_field = 'agent'
    producer_field = 'producer'

    def get_queryset(self):
        queryset = super().get_queryset()
        user = self.request.user

        if user.is_superuser:
            return queryset

        role = getattr(user, 'role', None)

        if role == Role.OWNER:
            return queryset

        if role == Role.AGENT:
            return self.filter_for_agent(queryset, user)

        if role == Role.PRODUCER:
            return self.filter_for_producer(queryset, user)

        return queryset.none()

    def filter_for_agent(self, queryset, user):
        agent = getattr(user, 'agent_profile', None)
        if agent is None or not self.agent_field:
            return queryset.none()
        return queryset.filter(**{self.agent_field: agent})

    def filter_for_producer(self, queryset, user):
        producer = getattr(user, 'producer_profile', None)
        if producer is None or not self.producer_field:
            return queryset.none()
        return queryset.filter(**{self.producer_field: producer})
