from django.contrib.auth.base_user import BaseUserManager


class UserManager(BaseUserManager):
    """User manager keyed by e-mail: this project has no `username` field."""

    use_in_migrations = True

    def _create_user(self, email, password, **extra_fields):
        if not email:
            raise ValueError('O e-mail é obrigatório.')

        email = self.normalize_email(email)
        user = self.model(email=email, **extra_fields)
        user.set_password(password)
        user.full_clean(exclude=['password'], validate_unique=False)
        user.save(using=self._db)
        return user

    def create_user(self, email, password=None, **extra_fields):
        extra_fields.setdefault('is_staff', False)
        extra_fields.setdefault('is_superuser', False)
        return self._create_user(email, password, **extra_fields)

    def create_superuser(self, email, password=None, **extra_fields):
        extra_fields.setdefault('is_staff', True)
        extra_fields.setdefault('is_superuser', True)
        extra_fields.setdefault('is_active', True)

        if extra_fields.get('is_staff') is not True:
            raise ValueError('O superusuário precisa ter is_staff=True.')
        if extra_fields.get('is_superuser') is not True:
            raise ValueError('O superusuário precisa ter is_superuser=True.')

        # A superuser operates across tenants, so it carries no tenant and no
        # role: TenantMiddleware exempts it and the admin uses `all_tenants`.
        extra_fields.setdefault('tenant', None)
        extra_fields.setdefault('role', '')

        return self._create_user(email, password, **extra_fields)
