from django.contrib.auth import views as auth_views
from django.urls import path

from accounts import views

app_name = 'accounts'

urlpatterns = [
    path('entrar/', views.EmailLoginView.as_view(), name='login'),
    path('sair/', views.AppLogoutView.as_view(), name='logout'),
    path('perfil/', views.ProfileView.as_view(), name='profile'),

    # Password reset, using Django's native views end to end.
    path(
        'senha/redefinir/',
        auth_views.PasswordResetView.as_view(
            template_name='accounts/password_reset.html',
            email_template_name='accounts/email/password_reset.txt',
            subject_template_name='accounts/email/password_reset_subject.txt',
            success_url='/conta/senha/redefinir/enviado/',
        ),
        name='password_reset',
    ),
    path(
        'senha/redefinir/enviado/',
        auth_views.PasswordResetDoneView.as_view(
            template_name='accounts/password_reset_done.html'
        ),
        name='password_reset_done',
    ),
    path(
        'senha/redefinir/<uidb64>/<token>/',
        auth_views.PasswordResetConfirmView.as_view(
            template_name='accounts/password_reset_confirm.html',
            success_url='/conta/senha/redefinir/concluido/',
        ),
        name='password_reset_confirm',
    ),
    path(
        'senha/redefinir/concluido/',
        auth_views.PasswordResetCompleteView.as_view(
            template_name='accounts/password_reset_complete.html'
        ),
        name='password_reset_complete',
    ),

    # Tenant user management, restricted to the OWNER.
    path('usuarios/', views.UserListView.as_view(), name='user_list'),
    path('usuarios/novo/', views.UserCreateView.as_view(), name='user_create'),
    path('usuarios/<int:pk>/editar/', views.UserUpdateView.as_view(), name='user_update'),
    path('convites/novo/', views.InvitationCreateView.as_view(), name='invitation_create'),

    # Public: the invitee has no account yet.
    path(
        'convite/<str:token>/',
        views.InvitationAcceptView.as_view(),
        name='invitation_accept',
    ),
]
