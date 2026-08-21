from django.contrib import messages
from django.contrib.auth import login
from django.contrib.auth.views import LoginView, LogoutView
from django.core.exceptions import PermissionDenied
from django.shortcuts import get_object_or_404, redirect
from django.urls import reverse_lazy
from django.views.generic import CreateView, DetailView, FormView, ListView, UpdateView

from accounts.forms import (
    EmailAuthenticationForm,
    InvitationAcceptForm,
    InvitationForm,
    UserCreateForm,
    UserUpdateForm,
)
from accounts.models import Invitation, User
from accounts.services import accept_invitation, send_invitation_email
from base.constants import Role
from base.mixins import TenantRequiredMixin


class EmailLoginView(LoginView):
    template_name = 'accounts/login.html'
    authentication_form = EmailAuthenticationForm
    redirect_authenticated_user = True


class AppLogoutView(LogoutView):
    pass


class OwnerRequiredMixin(TenantRequiredMixin):
    """Restrict a view to the tenant's OWNER."""

    def dispatch(self, request, *args, **kwargs):
        if request.user.is_authenticated and not request.user.is_superuser:
            if request.user.role != Role.OWNER:
                raise PermissionDenied('Apenas o dono da corretora pode gerenciar usuários.')
        return super().dispatch(request, *args, **kwargs)


class ProfileView(TenantRequiredMixin, DetailView):
    template_name = 'accounts/profile.html'
    context_object_name = 'profile_user'

    def get_object(self, queryset=None):
        return self.request.user


class UserListView(OwnerRequiredMixin, ListView):
    template_name = 'accounts/user_list.html'
    context_object_name = 'users'
    paginate_by = 25

    def get_queryset(self):
        return User.objects.filter(tenant=self.request.tenant).order_by('full_name')

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['invitations'] = Invitation.objects.filter(
            tenant=self.request.tenant
        ).order_by('-created_at')
        return context


class UserCreateView(OwnerRequiredMixin, CreateView):
    model = User
    form_class = UserCreateForm
    template_name = 'accounts/user_form.html'
    success_url = reverse_lazy('accounts:user_list')

    def get_form_kwargs(self):
        kwargs = super().get_form_kwargs()
        kwargs['tenant'] = self.request.tenant
        return kwargs

    def form_valid(self, form):
        messages.success(self.request, 'Usuário criado com sucesso.')
        return super().form_valid(form)


class UserUpdateView(OwnerRequiredMixin, UpdateView):
    model = User
    form_class = UserUpdateForm
    template_name = 'accounts/user_form.html'
    success_url = reverse_lazy('accounts:user_list')

    def get_queryset(self):
        return User.objects.filter(tenant=self.request.tenant)

    def form_valid(self, form):
        messages.success(self.request, 'Usuário atualizado com sucesso.')
        return super().form_valid(form)


class InvitationCreateView(OwnerRequiredMixin, CreateView):
    model = Invitation
    form_class = InvitationForm
    template_name = 'accounts/invitation_form.html'
    success_url = reverse_lazy('accounts:user_list')

    def get_form_kwargs(self):
        kwargs = super().get_form_kwargs()
        kwargs['tenant'] = self.request.tenant
        kwargs['invited_by'] = self.request.user
        return kwargs

    def form_valid(self, form):
        response = super().form_valid(form)
        send_invitation_email(self.request, self.object)
        messages.success(
            self.request, f'Convite enviado para {self.object.email}.'
        )
        return response


class InvitationAcceptView(FormView):
    """Public view: the invitee has no account yet."""

    template_name = 'accounts/invitation_accept.html'
    form_class = InvitationAcceptForm
    success_url = reverse_lazy('accounts:profile')

    def dispatch(self, request, *args, **kwargs):
        self.invitation = get_object_or_404(
            Invitation, token=kwargs['token'], accepted_at__isnull=True
        )
        if self.invitation.is_expired:
            return self.render_expired(request)
        return super().dispatch(request, *args, **kwargs)

    def render_expired(self, request):
        messages.error(request, 'Este convite expirou. Peça um novo à corretora.')
        return redirect('accounts:login')

    def get_form_kwargs(self):
        kwargs = super().get_form_kwargs()
        # SetPasswordForm validates the password against the user it will be
        # set on; the user only exists after the form is valid, so an unsaved
        # instance stands in for the validators.
        kwargs['user'] = User(
            email=self.invitation.email,
            tenant=self.invitation.tenant,
            role=self.invitation.role,
        )
        return kwargs

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['invitation'] = self.invitation
        return context

    def form_valid(self, form):
        user = accept_invitation(
            self.invitation,
            full_name=form.cleaned_data['full_name'],
            password=form.cleaned_data['new_password1'],
        )
        login(self.request, user)
        messages.success(self.request, f'Bem-vinda(o) à {user.tenant}.')
        return super().form_valid(form)
