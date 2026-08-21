from django import forms
from django.contrib.auth.forms import AuthenticationForm, SetPasswordForm

from accounts.models import Invitation, User
from base.constants import Role


class EmailAuthenticationForm(AuthenticationForm):
    """Login form labelled for e-mail, since there is no username."""

    username = forms.EmailField(
        label='E-mail',
        widget=forms.EmailInput(attrs={'autofocus': True, 'autocomplete': 'email'}),
    )

    error_messages = {
        'invalid_login': 'E-mail ou senha incorretos.',
        'inactive': 'Esta conta está inativa.',
    }


class UserCreateForm(forms.ModelForm):
    """Used by an OWNER to add a user directly, without the invitation flow."""

    class Meta:
        model = User
        fields = ['full_name', 'email', 'role', 'phone', 'is_active']
        labels = {'is_active': 'Ativo'}

    def __init__(self, *args, tenant=None, **kwargs):
        super().__init__(*args, **kwargs)
        self.tenant = tenant
        self.fields['role'].choices = Role.choices

    def clean_email(self):
        email = User.objects.normalize_email(self.cleaned_data['email'])
        if User.objects.filter(email__iexact=email).exists():
            raise forms.ValidationError('Já existe um usuário com este e-mail.')
        return email

    def save(self, commit=True):
        user = super().save(commit=False)
        user.tenant = self.tenant
        # No usable password: the user sets one through the password reset
        # flow or by accepting an invitation.
        user.set_unusable_password()
        if commit:
            user.save()
        return user


class UserUpdateForm(forms.ModelForm):
    class Meta:
        model = User
        fields = ['full_name', 'role', 'phone', 'is_active']
        labels = {'is_active': 'Ativo'}


class InvitationForm(forms.ModelForm):
    class Meta:
        model = Invitation
        fields = ['email', 'role']

    def __init__(self, *args, tenant=None, invited_by=None, **kwargs):
        super().__init__(*args, **kwargs)
        self.tenant = tenant
        self.invited_by = invited_by

    def clean_email(self):
        email = User.objects.normalize_email(self.cleaned_data['email'])

        if User.objects.filter(email__iexact=email, tenant=self.tenant).exists():
            raise forms.ValidationError('Este e-mail já pertence a um usuário da corretora.')

        pending = Invitation.objects.filter(
            tenant=self.tenant, email__iexact=email, accepted_at__isnull=True
        )
        if pending.exists():
            raise forms.ValidationError('Já existe um convite pendente para este e-mail.')

        return email

    def save(self, commit=True):
        invitation = super().save(commit=False)
        invitation.tenant = self.tenant
        invitation.invited_by = self.invited_by
        if commit:
            invitation.save()
        return invitation


class InvitationAcceptForm(SetPasswordForm):
    """Password definition when accepting an invitation."""

    full_name = forms.CharField(label='Nome completo', max_length=150)

    field_order = ['full_name', 'new_password1', 'new_password2']

    def save(self, commit=True):
        self.user.full_name = self.cleaned_data['full_name']
        return super().save(commit=commit)
