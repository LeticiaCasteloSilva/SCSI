from django.db import models
from django.utils.text import slugify

from base.models import TimeStampedModel
from base.validators import format_cnpj, validate_cnpj


def tenant_logo_upload_to(instance, filename):
    """Store logos under the tenant partition of the protected media root."""
    return f'tenant_{instance.pk or "new"}/core/logo/{filename}'


class Plan(TimeStampedModel):
    """Commercial plan. Only the Free plan is selectable in this phase."""

    name = models.CharField('nome', max_length=60)
    slug = models.SlugField('identificador', max_length=60, unique=True)
    price = models.DecimalField('preço', max_digits=10, decimal_places=2, default=0)
    is_enabled = models.BooleanField(
        'habilitado',
        default=False,
        help_text='Somente planos habilitados podem ser escolhidos no cadastro.',
    )
    max_users = models.PositiveIntegerField('limite de usuários', default=3)
    description = models.TextField('descrição', blank=True)

    class Meta:
        verbose_name = 'plano'
        verbose_name_plural = 'planos'
        ordering = ['price', 'name']

    def __str__(self):
        return self.name


class Tenant(TimeStampedModel):
    """A brokerage. Root of the shared-schema isolation: every domain row
    carries a foreign key to this model."""

    legal_name = models.CharField('razão social', max_length=200)
    trade_name = models.CharField('nome fantasia', max_length=200, blank=True)
    cnpj = models.CharField(
        'CNPJ',
        max_length=18,
        unique=True,
        validators=[validate_cnpj],
    )
    slug = models.SlugField('identificador', max_length=80, unique=True, blank=True)
    plan = models.ForeignKey(
        Plan,
        on_delete=models.PROTECT,
        related_name='tenants',
        verbose_name='plano',
    )
    email = models.EmailField('e-mail', blank=True)
    phone = models.CharField('telefone', max_length=20, blank=True)
    susep_code = models.CharField('código SUSEP', max_length=30, blank=True)
    logo = models.ImageField('logotipo', upload_to=tenant_logo_upload_to, blank=True)
    is_active = models.BooleanField('ativa', default=True)

    class Meta:
        verbose_name = 'corretora'
        verbose_name_plural = 'corretoras'
        ordering = ['legal_name']
        indexes = [
            models.Index(fields=['is_active'], name='tenant_is_active_idx'),
        ]

    def __str__(self):
        return self.trade_name or self.legal_name

    def clean(self):
        super().clean()
        if self.cnpj:
            self.cnpj = format_cnpj(self.cnpj)

    def save(self, *args, **kwargs):
        if self.cnpj:
            self.cnpj = format_cnpj(self.cnpj)
        if not self.slug:
            self.slug = self._build_unique_slug()
        super().save(*args, **kwargs)

    def _build_unique_slug(self):
        base_slug = slugify(self.trade_name or self.legal_name)[:70] or 'corretora'
        slug = base_slug
        suffix = 2
        while Tenant.objects.filter(slug=slug).exclude(pk=self.pk).exists():
            slug = f'{base_slug}-{suffix}'
            suffix += 1
        return slug
