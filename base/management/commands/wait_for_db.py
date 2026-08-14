import time

from django.conf import settings
from django.core.management.base import BaseCommand
from django.db import connections
from django.db.utils import OperationalError


class Command(BaseCommand):
    """Block until the database accepts connections.

    Runs before `migrate` and `runserver` so the application never starts
    against an unavailable database and fails silently later on.
    """

    help = 'Aguarda o banco de dados ficar disponivel antes de subir a aplicacao.'

    def add_arguments(self, parser):
        parser.add_argument(
            '--timeout',
            type=int,
            default=getattr(settings, 'WAIT_FOR_DB_TIMEOUT', 60),
            help='Tempo maximo de espera em segundos.',
        )
        parser.add_argument(
            '--interval',
            type=float,
            default=1.0,
            help='Intervalo entre tentativas em segundos.',
        )
        parser.add_argument(
            '--database',
            default='default',
            help='Alias da conexao a verificar.',
        )

    def handle(self, *args, **options):
        timeout = options['timeout']
        interval = options['interval']
        alias = options['database']

        self.stdout.write(f'Aguardando o banco de dados "{alias}"...')

        deadline = time.monotonic() + timeout
        attempt = 0
        last_error = None

        while time.monotonic() < deadline:
            attempt += 1
            try:
                connection = connections[alias]
                connection.ensure_connection()
            except OperationalError as error:
                last_error = error
                remaining = int(deadline - time.monotonic())
                self.stdout.write(
                    f'  tentativa {attempt}: indisponivel, '
                    f'nova tentativa em {interval}s ({remaining}s restantes)'
                )
                time.sleep(interval)
            else:
                self.stdout.write(
                    self.style.SUCCESS(
                        f'Banco de dados disponivel apos {attempt} tentativa(s).'
                    )
                )
                return

        self.stderr.write(
            self.style.ERROR(
                f'Banco de dados indisponivel apos {timeout}s. Ultimo erro: {last_error}'
            )
        )
        raise SystemExit(1)
