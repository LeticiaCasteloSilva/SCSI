from django.db import models


class Role(models.TextChoices):
    """Roles a user can hold inside a tenant.

    Declared in `base` because both `accounts.User` (which stores the role)
    and `base.mixins.RolePermissionMixin` (which enforces it) depend on it.
    """

    OWNER = 'OWNER', 'Dono'
    AGENT = 'AGENT', 'Agente'
    PRODUCER = 'PRODUCER', 'Produtor'
