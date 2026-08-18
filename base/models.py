from django.core.exceptions import ValidationError
from django.db import models

from base.managers import TenantManager


class TimeStampedModel(models.Model):
    """Abstract base model providing the audit fields required by every model."""

    created_at = models.DateTimeField('criado em', auto_now_add=True, db_index=True)
    updated_at = models.DateTimeField('atualizado em', auto_now=True)

    class Meta:
        abstract = True


class TenantAwareModel(TimeStampedModel):
    """Abstract base model of every domain entity.

    Injects the `tenant` foreign key that discriminates rows in the shared
    schema, and scopes the default manager to the tenant in context.
    """

    tenant = models.ForeignKey(
        'core.Tenant',
        on_delete=models.CASCADE,
        related_name='%(app_label)s_%(class)s_set',
        verbose_name='corretora',
        db_index=True,
    )

    # `objects` is declared first so it becomes the default manager used by
    # views, forms and the admin. `base_manager_name` points Django's internal
    # machinery (related descriptors, refresh_from_db) at the unscoped manager,
    # so framework internals never trip over the tenant filter.
    objects = TenantManager()
    all_tenants = models.Manager()

    class Meta:
        abstract = True
        base_manager_name = 'all_tenants'
        default_manager_name = 'objects'

    def clean(self):
        """Reject any foreign key pointing at another tenant's row."""
        super().clean()

        if self.tenant_id is None:
            return

        errors = {}
        for field in self._meta.concrete_fields:
            if not field.is_relation or field.name == 'tenant':
                continue
            if not issubclass(field.related_model, TenantAwareModel):
                continue

            related_id = getattr(self, field.attname, None)
            if related_id is None:
                continue

            related = field.related_model.all_tenants.filter(pk=related_id).first()
            if related is not None and related.tenant_id != self.tenant_id:
                errors[field.name] = ValidationError(
                    'Este registro pertence a outra corretora.',
                    code='cross_tenant',
                )

        if errors:
            raise ValidationError(errors)
