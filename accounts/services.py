from django.conf import settings
from django.core.mail import send_mail
from django.db import transaction
from django.template.loader import render_to_string
from django.urls import reverse
from django.utils import timezone

from accounts.models import User


def build_invitation_url(request, invitation):
    path = reverse('accounts:invitation_accept', kwargs={'token': invitation.token})
    return request.build_absolute_uri(path)


def send_invitation_email(request, invitation):
    """Send the invitation using Django's native mail backend."""
    context = {
        'invitation': invitation,
        'tenant': invitation.tenant,
        'accept_url': build_invitation_url(request, invitation),
        'role_display': invitation.get_role_display(),
    }
    subject = f'Convite para acessar a {invitation.tenant}'
    body = render_to_string('accounts/email/invitation.txt', context)

    send_mail(
        subject=subject,
        message=body,
        from_email=settings.DEFAULT_FROM_EMAIL,
        recipient_list=[invitation.email],
        fail_silently=False,
    )


@transaction.atomic
def accept_invitation(invitation, full_name, password):
    """Turn a pending invitation into an active user of the tenant."""
    user = User(
        email=invitation.email,
        full_name=full_name,
        tenant=invitation.tenant,
        role=invitation.role,
        is_active=True,
    )
    user.set_password(password)
    user.save()

    invitation.accepted_at = timezone.now()
    invitation.save(update_fields=['accepted_at', 'updated_at'])

    return user
