from django.db import models


class TimeStampedModel(models.Model):
    """Abstract base model providing the audit fields required by every model."""

    created_at = models.DateTimeField('criado em', auto_now_add=True, db_index=True)
    updated_at = models.DateTimeField('atualizado em', auto_now=True)

    class Meta:
        abstract = True
