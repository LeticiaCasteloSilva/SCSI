from django.http import JsonResponse
from django.views import View


class HealthCheckView(View):
    """Lightweight liveness probe.

    Deliberately touches no database and requires no authentication, so it
    stays answerable even while the rest of the stack is unavailable.
    """

    http_method_names = ['get', 'head']

    def get(self, request, *args, **kwargs):
        return JsonResponse({'status': 'ok'}, status=200)
