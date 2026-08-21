import secrets
from datetime import timedelta

from django.contrib.auth.base_user import AbstractBaseUser
from django.contrib.auth.models import PermissionsMixin
from django.core.exceptions import ValidationError
from django.db import models
from django.utils import timezone

from accounts.managers import UserManager
from base.constants import Role
from base.models import TimeStampedModel

INVITATION_VALID_DAYS = 7


def user_avatar_upload_to(instance, filename):
    """Store avatars under the tenant partition of the protected media root."""
    tenant_id = instance.tenant_id or 'none'
    return f'tenant_{tenant_id}/accounts/avatar/{filename}'


class User(AbstractBaseUser, PermissionsMixin, TimeStampedModel):
    """Authentication is by e-mail; there is no `username` field."""

    email = models.EmailField('e-mail', unique=True)
    full_name = models.CharField('nome completo', max_length=150)
    tenant = models.ForeignKey(
        'core.Tenant',
        on_delete=models.CASCADE,
        related_name='users',
        verbose_name='corretora',
        null=True,
        blank=True,
        help_text='Nulo apenas para superusuários, que operam entre corretoras.',
    )
    role = models.CharField('papel', max_length=20, choices=Role, blank=True)
    phone = models.CharField('telefone', max_length=20, blank=True)
    avatar = models.ImageField('avatar', upload_to=user_avatar_upload_to, blank=True)
    is_active = models.BooleanField('ativo', default=True)
    is_staff = models.BooleanField('acessa o admin', default=False)

    objects = UserManager()

    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = ['full_name']

    class Meta:
        verbose_name = 'usuário'
        verbose_name_plural = 'usuários'
        ordering = ['full_name']
        indexes = [
            models.Index(fields=['tenant', 'role'], name='user_tenant_role_idx'),
            models.Index(fields=['tenant', 'is_active'], name='user_tenant_active_idx'),
        ]

    def __str__(self):
        return f'{self.full_name} <{self.email}>'

    def clean(self):
        super().clean()
        self.email = UserManager.normalize_email(self.email)

        # Every non-superuser belongs to exactly one tenant and holds a role;
        # a superuser holds neither. Enforcing it here keeps TenantMiddleware
        # from ever meeting a user it cannot place.
        if self.is_superuser:
            return

        errors = {}
        if self.tenant_id is None:
            errors['tenant'] = 'Usuário não superusuário precisa de uma corretora.'
        if not self.role:
            errors['role'] = 'Usuário não superusuário precisa de um papel.'
        if errors:
            raise ValidationError(errors)

    def get_full_name(self):
        return self.full_name

    def get_short_name(self):
        return self.full_name.split(' ')[0] if self.full_name else self.email

    @property
    def is_owner(self):
        return self.role == Role.OWNER

    @property
    def is_agent(self):
        return self.role == Role.AGENT

    @property
    def is_producer(self):
        return self.role == Role.PRODUCER


def default_invitation_expiry():
    return timezone.now() + timedelta(days=INVITATION_VALID_DAYS)


def generate_invitation_token():
    return secrets.token_urlsafe(32)


class Invitation(TimeStampedModel):
    """Invitation for a new user to join a tenant with a given role."""

    tenant = models.ForeignKey(
        'core.Tenant',
        on_delete=models.CASCADE,
        related_name='invitations',
        verbose_name='corretora',
    )
    email = models.EmailField('e-mail')
    role = models.CharField('papel', max_length=20, choices=Role)
    token = models.CharField(
        'token', max_length=64, unique=True, default=generate_invitation_token
    )
    expires_at = models.DateTimeField('expira em', default=default_invitation_expiry)
    accepted_at = models.DateTimeField('aceito em', null=True, blank=True)
    invited_by = models.ForeignKey(
        'accounts.User',
        on_delete=models.SET_NULL,
        related_name='sent_invitations',
        verbose_name='convidado por',
        null=True,
        blank=True,
    )

    class Meta:
        verbose_name = 'convite'
        verbose_name_plural = 'convites'
        ordering = ['-created_at']
        constraints = [
            models.UniqueConstraint(
                fields=['tenant', 'email'],
                condition=models.Q(accepted_at__isnull=True),
                name='unique_pending_invitation_per_tenant_email',
            ),
        ]
        indexes = [
            models.Index(fields=['tenant', 'accepted_at'], name='invite_tenant_state_idx'),
        ]

    def __str__(self):
        return f'{self.email} ({self.get_role_display()})'

    @property
    def is_accepted(self):
        return self.accepted_at is not None

    @property
    def is_expired(self):
        return timezone.now() > self.expires_at

    @property
    def is_pending(self):
        return not self.is_accepted and not self.is_expired

    @property
    def status_label(self):
        if self.is_accepted:
            return 'Aceito'
        if self.is_expired:
            return 'Expirado'
        return 'Pendente'
